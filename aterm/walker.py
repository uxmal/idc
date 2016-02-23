'''Term walking.

A term walker is a class aimed to process/transform a term as it traverses the
term. It is an extension of the Visitor design pattern.

An term walker's interface is very liberal: is up to the caller determine which
method to call and which arguments to pass, and the return value is not
necessarily a term.

As a walker may change its context as it traverses the tree, sucessive calls to
the same walker methods do not necessarily yield the same results.
'''


import inspect

from aterm import visitor
from aterm import convert


class _Dispatcher(visitor.Visitor):
	'''Visitor which dynamically resolves the walker method name corresponding 
	to the term being dispatched.
	'''
	
	def __init__(self, walker, prefix):
		visitor.Visitor.__init__(self)
		self.walker = walker
		self.prefix = prefix

	def __call__(self, term, *args, **kargs):
		method, targs = self.visit(term)
		return method(*(targs + args), **kargs)

	def getmethod(self, suffix):
		return getattr(self.walker, self.prefix + suffix)
		
	def visitTerm(self, term):
		try:
			return self.getmethod('_Term'), (term,)
		except AttributeError:
			raise ValueError('%s.%s: cannot dispatch term: %r' % (
					self.walker.__class__.__name__,
					self.prefix,
					term
				)
			)
	
	def visitLit(self, term):
		try:
			return self.getmethod('_Lit'), (term.value,)
		except AttributeError:
			return self.visitTerm(term)
	
	def visitInt(self, term):
		try:
			return self.getmethod('_Int'), (term.value,)
		except AttributeError:
			return self.visitLit(term)
			
	def visitReal(self, term):
		try:
			return self.getmethod('_Real'), (term.value,)
		except AttributeError:
			return self.visitLit(term)
	
	def visitStr(self, term):
		try:
			return self.getmethod('_Str'), (term.value,)
		except AttributeError:
			return self.visitLit(term)
	
	def visitList(self, term):
		try:
			return self.getmethod('_List'), (term,)
		except AttributeError:
			return self.visitTerm(term)
	
	def visitNil(self, term):
		try:
			return self.getmethod('_Nil'), ()
		except AttributeError:
			return self.visitList(term)
	
	def visitCons(self, term):
		try:
			return self.getmethod('_Cons'), (term.head, term.tail)
		except AttributeError:
			return self.visitList(term)
	
	def visitAppl(self, term):
		try:
			return self.getmethod(term.name), tuple(term.args)
		except AttributeError:
			try:
				return self.getmethod('_Appl'), (term.name, term.args)
			except AttributeError:
				return self.visitTerm(term)
				

class Dispatch(object):
	'''Descriptor which dispatches a term to a method with a name starting 
	with the given prefix, and a suffix determined from the term.
		
	Suffixes are (listed by the order their are tried):
	 - "Name" for a "Name" application term
	 - "_Int" for an integer term
	 - "_Real" for a real term
	 - "_Str" for a string term
	 - "_Lit" for a generic literal term
	 - "_Nil" for a nil list term
	 - "_Cons" for a cons list term
	 - "_List" for a generic list term
	 - "_Appl" for a generic application term
	 - "_Term" for a generic term
	'''
	
	def __init__(self, prefix, doc = None):
		self.prefix = prefix
		self.__doc__ = doc
		
	def __get__(self, obj, objtype):
		return _Dispatcher(obj, self.prefix)
	

class Walker(object):
	'''Base class for term walkers.'''

	def __init__(self):
		pass

	# TODO: handle annotations?
	# TODO: pass the term arg?
	
	def _int(self, term):
		'''Get the value of an integer term.'''
		return convert.toInt(term)
	
	def _real(self, term):
		'''Get the value of a real term.'''
		return convert.toReal(term)
	
	def _str(self, term):
		'''Get the value of a string term.'''
		return convert.toStr(term)
	
	def _lit(self, term):
		'''Get the value of a literal term.'''
		return convert.toLit(term)
	
	def _obj(self, term):
		return convert.toObj(term)

	# XXX: is this actually useful?
	def _match(self, term, pattern):
		'''Match the term against the given pattern. Variables are stored in 
		the caller's local namespace.
		'''
		match = term.rmatch(pattern)
		if match:
			caller = inspect.currentframe().f_back
			caller.f_locals.update(match.kargs)
			return True
		else:
			return False

	# TODO: implement methods for collecting terms?
	
