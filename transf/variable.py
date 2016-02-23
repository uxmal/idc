'''Variable.'''


from transf import transformation
from transf import context


class Variable(object):
	'''Base class for context variables.

	Although this class defines the interface of some basic and common variable
	operations, the semantics of some of these operations are ocasionally specific
	to each of the derived class. Derived classes are also free to provide more
	variable operations, and the corresponding transformations.
	'''

	__slots__ = ['name']

	def __init__(self, name = None):
		self.binding = context.Local(name)

	def __repr__(self):
		name = self.__class__.__module__ + '.' + self.__class__.__name__
		return '<%s name=%s>' % (name, self.binding)


class _VariableTransformation(transformation.Transformation):

	def __init__(self, binding, method):
		transformation.Transformation.__init__(self)
		self.binding = binding
		self.method = method
		self.__doc__ = method.__doc__

	def apply(self, trm, ctx):
		return self.method(self.binding, trm, ctx)


def VariableTransformation(method):
	'''Decorator to simplify the definition of transformation
	as variable methods.'''
	def get_transformation(self):
		return _VariableTransformation(self.binding, method)
	get_transformation.__name__ = "get_" + method.__name__
	return property(get_transformation, doc=method.__doc__)


class _VariableTransformation2(transformation.Transformation):

	def __init__(self, binding, method, args, kargs):
		transformation.Transformation.__init__(self)
		self.binding = binding
		self.method = method
		self.args = args
		self.kargs = kargs
		self.__doc__ = method.__doc__

	def apply(self, trm, ctx):
		return self.method(self.binding, trm, ctx)


def VariableTransformationFactory(method):
	'''Decorator to simplify the definition of transformation
	as variable methods.'''
	def get_transformation(self, *args, **kargs):
		return _VariableTransformation2(self.binding, method, args, kargs)
	get_transformation.__name__ = method.__name__
	get_transformation.__doc__ = method.__doc__
	return get_transformation

