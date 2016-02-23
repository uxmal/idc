'''Module for handling assembly language code.'''


from transf import transformation
from transf import parse

from machine.pentium.registers import *


class Temp(transformation.Transformation):
	"""Transformation which generates an unique temporary variable name."""

	tmp_no = 0

	def apply(self, trm, ctx):
		self.tmp_no += 1
		name = "tmp%d" % self.tmp_no
		return trm.factory.make("Sym(_){Tmp}", name)

temp =  Temp()


parse.Transfs('''

Word(size) =
	!Int(<size>,NoSign)

UWord(size) =
	!Int(<size>,Unsigned)

SWord(size) =
	!Int(<size>,Signed)

false = !Lit(Bool,0)
true = !Lit(Bool,1)


ZeroFlag(size, res) =
	!Assign(Bool, <zf>, Binary(Eq(<Word(size)>), <res>, Lit(<Word(size)>,0)))

Negative(size, op) =
	!Binary(Lt(<SWord(size)>), <op>, Lit(<SWord(size)>,0))

NonNegative(size, op) =
	!Binary(GtEq(<SWord(size)>), <op>, Lit(<SWord(size)>,0))

SignFlag(size, res) =
	!Assign(Bool, <sf>, <Negative(size, res)>)

HsbOne(size, op) =
	!Binary(RShift(<UWord(size)>),<op>,Lit(<UWord(size)>,<arith.DecInt(size)>))

HsbZero(size, op) =
	!Unary(Not(Bool),<HsbOne(size,op)>)


LNot(op1) = !Unary(Not(Bool),<op1>)
LAnd(op1,op2) = !Binary(And(Bool),<op1>,<op2>)
LOr(op1,op2) = !Binary(Or(Bool),<op1>,<op2>)
LEq(op1,op2) = !Binary(Eq(Bool),<op1>,<op2>)
LNotEq(op1,op2) = !Binary(NotEq(Bool),<op1>,<op2>)


''')
