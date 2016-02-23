'''Base transformation classes.'''


#import warnings

import aterm.factory
import aterm.term

from transf import context


class Transformation(object):
	'''Abstract class for term transformations.

	A transformation takes as input a term and returns the transformed term, or
	raises a failure exception if it is not applicable. It also receives a
	transformation context to which it can read/write.

	A transformation should B{not} maintain any state itself, i.e., different calls
	to the L{apply} method with the same term and context must produce the same
	result.
	'''

	__slots__ = []

	def __init__(self):
		'''Constructor.'''
		pass

	def __call__(self, trm, **kargs):
		'''User-friendly wrapper for L{apply}.'''
		if isinstance(trm, basestring):
			trm = aterm.factory.factory.parse(trm)
		from transf.types import term
		vrs = [(name, term.Term(value)) for name, value in kargs.iteritems()]
		ctx = context.Context(vrs)
		return self.apply(trm, ctx)

	def apply(self, trm, ctx):
		'''Applies the transformation to the given term with the specified context.

		@param trm: L{Term<aterm.term.Term>} to be transformed.
		@param ctx: Transformation L{context<context.Context>}.
		@return: The transformed term on success.
		@raise exception.Failure: on failure.
		'''
		raise NotImplementedError

	def __neg__(self):
		'''Negation operator. Shorthand for L{lib.combine.Not}'''
		#warnings.warn("using deprecated negation operator", DeprecationWarning, stacklevel=2)
		from transf.lib import combine
		return combine.Not(self)

	def __pos__(self):
		'''Positive operator. Shorthand for L{lib.combine.Try}'''
		#warnings.warn("using deprecated try operator", DeprecationWarning, stacklevel=2)
		from transf.lib import combine
		return combine.Try(self)

	def __add__(self, other):
		'''Addition operator. Shorthand for L{lib.combine.Choice}'''
		#warnings.warn("using deprecated choice operator", DeprecationWarning, stacklevel=2)
		from transf.lib import combine
		return combine.Choice(self, other)

	def __mul__(self, other):
		'''Multiplication operator. Shorthand for L{lib.combine.Composition}'''
		#warnings.warn("using deprecated composition operator", DeprecationWarning, stacklevel=2)
		from transf.lib import combine
		return combine.Composition(self, other)

	def __pow__(self, other):
		'''Exponentiation operater. Shorthand for L{lib.combine.GuardedChoice}.

		For example, C{t1 **t2** t3} is equivalent, to C{lib.combine.GuardedChoice(t1, t2,
		t3)}. The exponentiation operator is right associative, so C{t1 **t2** t3
		**t4** t5} is the same as C{t1 **t2** (t3 **t4** t5)}. However note that its
		precedence is higher than other operators, therefore parenthesis must be used
		around them.

		@see: U{http://docs.python.org/ref/summary.html} for a summary of Python's
		operators precedence.
		'''
		#warnings.warn("using deprecated guarded choice operator", DeprecationWarning, stacklevel=2)
		from transf.lib import combine
		if isinstance(other, tuple):
			return combine.GuardedChoice(self, *other)
		else:
			return (self, other)

	def __repr__(self):
		name = self.__class__.__module__ + '.' + self.__class__.__name__
		attrs = {}
		for objname in dir(self):
			obj = getattr(self, objname)
			if isinstance(obj, (Transformation, aterm.term.Term)):
				try:
					objrepr = repr(obj)
				except:
					objrepr = "<error>"
				attrs[objname] = objrepr
		names = attrs.keys()
		names.sort()
		return '<' + name + '(' + ', '.join(["%s=%s" % (name, attrs[name]) for name in names]) + ')>'

