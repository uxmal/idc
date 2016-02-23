'''Base classes for transformations operators.'''


from transf import transformation


class UnaryMixin(object):
	'''Base mix-in class for unary operations on transformations.'''

	__slots__ = ['operand']

	def __init__(self, operand):
		assert isinstance(operand, transformation.Transformation)
		self.operand = operand


class BinaryMixin(object):
	'''Base mix-in class for binary operations on transformations.'''

	__slots__ = ['loperand', 'roperand']

	def __init__(self, loperand, roperand):
		assert isinstance(loperand, transformation.Transformation)
		assert isinstance(roperand, transformation.Transformation)
		self.loperand = loperand
		self.roperand = roperand


class TernaryMixin(object):
	'''Base mix-in class for ternary operations on transformations.'''

	__slots__ = ['operand1', 'operand2', 'operand3']

	def __init__(self, operand1, operand2, operand3):
		assert isinstance(operand1, transformation.Transformation)
		assert isinstance(operand2, transformation.Transformation)
		assert isinstance(operand3, transformation.Transformation)
		self.operand1 = operand1
		self.operand2 = operand2
		self.operand3 = operand3


class Unary(transformation.Transformation, UnaryMixin):
	'''Base class for unary operations on transformations.'''

	__slots__ = []

	def __init__(self, operand):
		transformation.Transformation.__init__(self)
		UnaryMixin.__init__(self, operand)


class Binary(transformation.Transformation, BinaryMixin):
	'''Base class for binary operations on transformations.'''

	__slots__ = []

	def __init__(self, loperand, roperand):
		transformation.Transformation.__init__(self)
		BinaryMixin.__init__(self, loperand, roperand)


class Ternary(transformation.Transformation, TernaryMixin):
	'''Base class for ternary operations on transformations.'''

	__slots__ = []

	def __init__(self, operand1, operand2, operand3):
		transformation.Transformation.__init__(self)
		TernaryMixin.__init__(self, operand1, operand2, operand3)


def _NaryIter(loperands_iter, Binary, roperand):
	try:
		loperand = loperands_iter.next()
	except StopIteration:
		return roperand
	else:
		return Binary(loperand, Nary(loperands_iter, Binary, roperand))

def Nary(loperands, Binary, roperand):
	'''Build a N-ary by the right-association of binary operators.'''
	return _NaryIter(iter(loperands), Binary, roperand)
