'''Term building from patterns.'''


from aterm.factory import factory
from aterm import exception
from aterm import convert
from aterm import parser


class Build(object):
	'''Build context.'''

	def __init__(self, args, kargs):
		self.args = args
		self.kargs = kargs


class Builder(object):
	'''Base class for all term builders.'''

	def build(self, *args, **kargs):
		build = Build(list(args), kargs)
		return self._build(build)

	def _build(self, build):
		raise NotImplementedError


class Term(Builder):
	'''Builds a term. Used for building terminal terms such as
	the literal terms and empty list terms.
	'''

	def __init__(self, term):
		Builder.__init__(self)
		self.term = term

	def _build(self, build):
		return self.term


def Int(value):
	'''Integer term builder.'''
	return Term(factory.makeInt(value))


def Real(value):
	'''Real term builder.'''
	return Term(factory.makeReal(value))


def Str(value):
	'''String term builder.'''
	return Term(factory.makeStr(value))


def Nil():
	'''Empty list term builder.'''
	return Term(factory.makeNil())


class Cons(Builder):
	'''List construction term builder.'''

	def __init__(self, head, tail):
		Builder.__init__(self)
		assert isinstance(head, Builder)
		assert isinstance(tail, Builder)
		self.head = head
		self.tail = tail

	def _build(self, build):
		return factory.makeCons(
			self.head._build(build),
			self.tail._build(build)
		)


class Appl(Builder):
	'''Application term builder.'''

	def __init__(self, name, args, annos):
		Builder.__init__(self)
		assert isinstance(name, basestring)
		assert isinstance(annos, Builder)
		self.name = name
		self.args = tuple(args)
		self.annos = annos

	def _build(self, build):
		return factory.makeAppl(
			self.name,
			[arg._build(build) for arg in self.args],
			self.annos._build(build)
		)


class ApplCons(Builder):
	'''Application (construction) term builder.

	Same as L{Appl}, but receives name and arguments from other builders.
	'''

	def __init__(self, name, args, annos):
		Builder.__init__(self)
		assert isinstance(name, Builder)
		assert isinstance(args, Builder)
		assert isinstance(annos, Builder)
		self.name = name
		self.args = args
		self.annos = annos

	def _build(self, build):
		name = convert.toStr(self.name._build(build))
		args = convert.toList(self.args._build(build))
		annos = self.annos._build(build)
		return factory.makeAppl(name, args)


class Wildcard(Builder):
	'''Wildcard term builder. Gets the term from the supplied
	argument list.'''

	def _build(self, build):
		return build.args.pop(0)


class Var(Builder):
	'''Variable term builder. Gets the from the supplied
	argument dictionary.'''

	def __init__(self, name):
		Builder.__init__(self)
		assert isinstance(name, basestring)
		self.name = name

	def _build(self, build):
		return build.kargs[self.name]


class Parser(parser.Parser):
	'''Parse a term pattern into a tree of term builders.'''

	def handleInt(self, value):
		return Int(value)

	def handleReal(self, value):
		return Real(value)

	def handleStr(self, value):
		return Str(value)

	def handleNil(self):
		return Nil()

	def handleCons(self, head, tail):
		return Cons(head, tail)

	def handleAppl(self, name, args, annos = Nil()):
		return Appl(name, args, annos)

	def handleWildcard(self):
		return Wildcard()

	def handleVar(self, name):
		return Var(name)

	def handleApplCons(self, name, args, annos = Nil()):
		return ApplCons(name, args, annos)
