'''Term creation.'''


import antlr

from aterm import exception
from aterm import term
from aterm import lexer
from aterm import parser


class _Singleton(type):
	'''Metaclass for the Singleton design pattern. Based on
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/102187
	'''

	def __init__(mcs, name, bases, dic):
		super(_Singleton, mcs).__init__(name, bases, dic)
		mcs.__instance = None

	def __call__(mcs, *args, **kargs):
		if mcs.__instance is None:
			mcs.__instance = super(_Singleton, mcs).__call__(*args, **kargs)
		return mcs.__instance


class Factory(object):
	'''This class is responsible for make new terms, either by parsing
	from strings or streams, or via one the of the "make" methods.'''

	__metaclass__ = _Singleton

	# TODO: implement maximal sharing

	MAX_PARSE_CACHE_LEN = 512

	# TODO: cache match and build patterns too

	def __init__(self):
		self.parseCache = {}
		self.__nil = term.Nil(self)

	def makeInt(self, value):
		'''Creates a new integer literal term'''
		return term.Integer(self, value)

	def makeReal(self, value):
		'''Creates a new real literal term'''
		return term.Real(self, value)

	def makeStr(self, value):
		'''Creates a new string literal term'''
		return term.Str(self, value)

	def makeNil(self):
		'''Creates a new empty list term'''
		return self.__nil

	def makeCons(self, head, tail):
		'''Creates a new extended list term'''
		return term.Cons(self, head, tail)

	def makeList(self, seq):
		'''Creates a new list from a sequence.'''
		accum = self.makeNil()
		for elm in reversed(seq):
			accum = self.makeCons(elm, accum)
		return accum

	def makeTuple(self, args = None, annotations = None):
		'''Creates a new tuple term'''
		return self.makeAppl("", args, annotations)

	def makeAppl(self, name, args = None, annotations = None):
		'''Creates a new application term'''
		if args is None:
			args = ()
		if annotations is None:
			annotations = self.makeNil()
		return term.Appl(self, name, args, annotations)

	def coerce(self, value, name = None):
		'''Coerce an object to a term. Value must be an int, a float, a string,
		a sequence of terms, or a term.'''

		if isinstance(value, term.Term):
			return value
		elif isinstance(value, (int, long)):
			return self.makeInt(value)
		elif isinstance(value, float):
			return self.makeReal(value)
		elif isinstance(value, basestring):
			return self.makeStr(value)
		elif isinstance(value, list):
			return self.makeList(value)
		elif isinstance(value, tuple):
			return self.makeList(value)
		else:
			msg = "argument"
			if not name is None:
				msg += " " + name
			msg += " is neither a term, a literal, or a list: "
			msg += repr(value)
			raise TypeError(msg)

	def _parse(self, lexer):
		'''Creates a new term by parsing a string.'''

		p = Parser(lexer)
		try:
			return p.term()
		except antlr.ANTLRException, exc:
			raise exception.ParseError(str(exc))

	def readFromTextFile(self, fp):
		'''Creates a new term by parsing from a text stream.'''

		return self._parse(lexer.Lexer(fp = fp))

	def parse(self, buf):
		'''Creates a new term by parsing a string.'''

		try:
			return self.parseCache[buf]
		except KeyError:
			pass

		result = self._parse(lexer.Lexer(buf))

		if len(self.parseCache) > self.MAX_PARSE_CACHE_LEN:
			# TODO: use a LRU cache policy
			self.parseCache.clear()
		self.parseCache[buf] = result

		return result

	def match(self, pattern, term):
		'''Matches the term to a string pattern and a list of arguments.
		'''
		assert isinstance(pattern, basestring)
		from aterm.match import Parser, Match
		p = Parser(lexer.Lexer(pattern))
		try:
			matcher = p.term()
		except antlr.ANTLRException, exc:
			raise exception.ParseError(str(exc))
		mo = Match()
		if matcher.visit(term, mo):
			return mo
		else:
			return None

	def make(self, pattern, *args, **kargs):
		'''Creates a new term from a string pattern and a list of arguments.
		First the string pattern is parsed, then the holes in
		the pattern are filled with the supplied arguments.
		'''
		assert isinstance(pattern, basestring)
		from aterm.build import Parser
		p = Parser(lexer.Lexer(pattern))
		try:
			builder = p.term()
		except antlr.ANTLRException, exc:
			raise exception.ParseError(str(exc))

		i = 0
		_args = []
		for i in range(len(args)):
			_args.append(self.coerce(args[i], str(i)))
			i += 1

		_kargs = {}
		for name, value in kargs.iteritems():
			_kargs[name] = self.coerce(value, "'" + name + "'")

		return builder.build(*_args, **_kargs)


factory = Factory()


class Parser(parser.Parser):
	'''Parse a textual description of the term.'''

	def handleInt(self, value):
		return factory.makeInt(value)

	def handleReal(self, value):
		return factory.makeReal(value)

	def handleStr(self, value):
		return factory.makeStr(value)

	def handleNil(self):
		return factory.makeNil()

	def handleCons(self, head, tail):
		return factory.makeCons(head, tail)

	def handleAppl(self, name, args, annos = None):
		return factory.makeAppl(name, args, annos)

	def handleWildcard(self):
		raise exception.ParseError('wildcard in term')

	def handleVar(self, name):
		raise exception.ParseError('variable in term')

	def handleApplCons(self, name, args, annos = None):
		assert False
