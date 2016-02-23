'''Utilitary transformations.'''


from transf import exception
from transf import transformation


class Adaptor(transformation.Transformation):
	'''Transformation adapter for a regular function.'''

	def __init__(self, func):
		transformation.Transformation.__init__(self)
		self.func = func
		self.__doc__ = func.__doc__

	def apply(self, trm, ctx):
		trm = self.func(trm)
		if trm is None:
			raise exception.Failure
		else:
			return trm


class BoolAdaptor(Adaptor):
	'''Transformation adapter for a boolean function.'''

	def apply(self, trm, ctx):
		if self.func(trm):
			return trm
		else:
			raise exception.Failure


class Proxy(transformation.Transformation):
	'''Defers the transformation to another transformation, which does not
	need to be specified at initialization time.
	'''

	__slots__ = ['subject']

	def __init__(self, subject = None):
		transformation.Transformation.__init__(self)
		self.subject = subject

	def apply(self, trm, ctx):
		if self.subject is None:
			raise exception.Fatal('subject transformation not specified')
		return self.subject.apply(trm, ctx)

	def __repr__(self):
		return '<%s ...>' % (self.__class__.__name__,)

