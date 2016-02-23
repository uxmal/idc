'''Arithmetic transformations.'''


import aterm

from transf import exception
from transf import transformation
from transf import operate
from transf.lib import base
from transf.lib import project


# TODO: complete


class _Unary(operate.Unary):

	def __init__(self, operand, func):
		operate.Unary.__init__(self, operand)
		self.func = func

	def apply(self, term, ctx):
		x = self.operand.apply(term, ctx)
		try:
			return self.func(term,x)
		except TypeError:
			raise exception.Failure('wrong term type', x)


class _Binary(operate.Binary):

	def __init__(self, loperand, roperand, func):
		operate.Binary.__init__(self, loperand, roperand)
		self.func = func

	def apply(self, term, ctx):
		x = self.loperand.apply(term, ctx)
		y = self.roperand.apply(term, ctx)
		try:
			return self.func(term,x,y)
		except TypeError:
			raise exception.Failure('wrong term type', x, y)



# TODO: use decorators and/or metaclasses to simplify this

_fnNegInt = lambda t, x: t.factory.makeInt(-int(x))
_fnIncInt = lambda t, x: t.factory.makeInt(int(x) + 1)
_fnDecInt = lambda t, x: t.factory.makeInt(int(x) - 1)

NegInt = lambda o: _Unary(o, _fnNegInt)
IncInt = lambda o: _Unary(o, _fnIncInt)
DecInt = lambda o: _Unary(o, _fnDecInt)

_fnAddInt = lambda t, x, y: t.factory.makeInt(int(x) + int(y))
_fnSubInt = lambda t, x, y: t.factory.makeInt(int(x) + int(y))
_fnMulInt = lambda t, x, y: t.factory.makeInt(int(x) * int(y))
_fnDivInt = lambda t, x, y: t.factory.makeInt(int(x) / int(y))

AddInt = lambda l, r: _Binary(l, r, _fnAddInt)
SubInt = lambda l, r: _Binary(l, r, _fnSubInt)
MulInt = lambda l, r: _Binary(l, r, _fnMulInt)
DivInt = lambda l, r: _Binary(l, r, _fnDivInt)

def _fnBool(t, b):
	if b:
		return t
	else:
		raise exception.Failure

_fnEqInt = lambda t, x, y: _fnBool(t, int(x) == int(y))
_fnNeqInt = lambda t, x, y: _fnBool(t, int(x) != int(y))
_fnGtInt = lambda t, x, y: _fnBool(t, int(x) > int(y))
_fnLtInt = lambda t, x, y: _fnBool(t, int(x) > int(y))
_fnGeqInt = lambda t, x, y: _fnBool(t, int(x) >= int(y))
_fnLeqInt = lambda t, x, y: _fnBool(t, int(x) <= int(y))

EqInt = lambda l, r: _Binary(l, r, _fnEqInt)
NeqInt = lambda l, r: _Binary(l, r, _fnNeqInt)
GtInt = lambda l, r: _Binary(l, r, _fnGtInt)
LtInt = lambda l, r: _Binary(l, r, _fnLtInt)
GeqInt = lambda l, r: _Binary(l, r, _fnGeqInt)
LeqInt = lambda l, r: _Binary(l, r, _fnLeqInt)

Neg = NegInt
Inc = IncInt
Dec = DecInt
Add = AddInt
Sub = SubInt
Mul = MulInt
Div = DivInt
Eq = EqInt
Neq = NeqInt
Gt = GtInt
Lt = LtInt
Geq = GeqInt
Leq = LeqInt

add = Add(project.first, project.second)


class Count(transformation.Transformation):

	def __init__(self):
		transformation.Transformation.__init__(self)
		self.value = 0

	def apply(self, trm, ctx):
		self.value += 1
		trm = trm.factory.makeInt(self.value)
		return trm





