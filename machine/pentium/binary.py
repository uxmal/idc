'''Binary arithmetic instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''


AddFlags(size, op1, op2, res) =
	![
		<ZeroFlag(size, res)>,
		<SignFlag(size, res)>,
		Assign(Bool, <cf>,
			Binary(Or(Bool),
				Binary(And(Bool),<HsbOne(size,op1)>,<HsbOne(size,op2)>),
				Binary(And(Bool),
					<HsbZero(size,res)>,
					Binary(Or(Bool),<HsbOne(size,op1)>,<HsbOne(size,op2)>)
				)
			)
		),
		Assign(Bool, <of>,
			Binary(Or(Bool),
				Binary(And(Bool),
					Binary(And(Bool),<Negative(size,op1)>,<Negative(size,op2)>),
					<NonNegative(size,res)>
				),
				Binary(And(Bool),
					Binary(And(Bool),<NonNegative(size,op1)>,<NonNegative(size,op2)>),
					<Negative(size,res)>
				)
			)
		)
	]

SubFlags(size, op1, op2, res) =
	![
		<ZeroFlag(size, res)>,
		<SignFlag(size, res)>,
		Assign(Bool, <cf>,
			Binary(Or(Bool),
				Binary(And(Bool),<HsbZero(size,op1)>,<HsbOne(size,op2)>),
				Binary(And(Bool),
					<HsbZero(size,res)>,
					Binary(Or(Bool),<HsbZero(size,op1)>,<HsbOne(size,op2)>)
				)
			)
		),
		Assign(Bool, <of>,
			Binary(Or(Bool),
				Binary(And(Bool),
					Binary(And(Bool),<NonNegative(size,op1)>,<Negative(size,op2)>),
					<NonNegative(size,res)>
				),
				Binary(And(Bool),
					Binary(And(Bool),<Negative(size,op1)>,<NonNegative(size,op2)>),
					<Negative(size,res)>
				)
			)
		)
	]

AsmAdd(size) =
		[dst, src] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Plus(type), dst, src)),
			*<AddFlags(size, !tmp, !src, !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp


asmADDB = AsmAdd(!8)
asmADDW = AsmAdd(!16)
asmADDL = AsmAdd(!32)


AsmADC(size) =
		[dst, src] -> [
			Assign(type, tmp, dst),
			Assign(type, dst,
				Binary(Plus(type),dst,
					Binary(Plus(type),src,
						Cond(<cf>,Lit(type,1),Lit(type,0))))),
			*<AddFlags(size, !tmp, !src, !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp


asmADCB = AsmADC(!8)
asmADCW = AsmADC(!16)
asmADCL = AsmADC(!32)


AsmSub(size) =
		[dst, src] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Minus(type), dst, src)),
			*<SubFlags(size, !tmp, !src, !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmSUBB = AsmSub(!8)
asmSUBW = AsmSub(!16)
asmSUBL = AsmSub(!32)


AsmSBB(size) =
		[dst, src] -> [
			Assign(type, tmp, dst),
			Assign(type, dst,
				Binary(Minus(type),dst,
					Binary(Plus(type),src,
						Cond(<cf>,Lit(type,1),Lit(type,0))))),
			*<SubFlags(size, !tmp, !src, !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmSBBB = AsmSBB(!8)
asmSBBW = AsmSBB(!16)
asmSBBL = AsmSBB(!32)


AsmInc(size) =
		[dst] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Plus(type), dst, Lit(type,1))),
			*<AddFlags(size, !tmp, !Lit(type,1), !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmINCB = AsmInc(!8)
asmINCW = AsmInc(!16)
asmINCL = AsmInc(!32)

AsmDec(size) =
		[dst] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Binary(Minus(type), dst, Lit(type,1))),
			*<SubFlags(size, !tmp, !Lit(type,1), !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmDECB = AsmDec(!8)
asmDECW = AsmDec(!16)
asmDECL = AsmDec(!32)


HighLow(size) =
	switch size
		case 8: ![<ah>,<al>]
		case 16: ![<dx>,<ax>]
		case 32: ![<edx>,<eax>]
	end

AsmMUL(size) =
		[src] -> <
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp, Binary(Mult(type2),Cast(type2,low),Cast(type2,src))),
			Assign(type, low, Cast(type,tmp)),
			Assign(type, high, Cast(type,Binary(RShift(type),tmp,Lit(type2,<size>)))),
			Assign(Bool, <cf>, Binary(NotEq(type),high,Lit(type2,0))),
			Assign(Bool, <of>, Binary(NotEq(type),high,Lit(type2,0)))
		]>
	where
		type := Word(size) ;
		type2 := Word(arith.MulInt(size,!2)) ;
		tmp := temp

asmMULB = AsmMUL(!8)
asmMULW = AsmMUL(!16)
asmMULL = AsmMUL(!32)


AsmIMUL1(size,src) =
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp, Binary(Mult(type2),Cast(type2,low),Cast(type2,<src>))),
			Assign(type, low, Cast(type,tmp)),
			Assign(type, high, Cast(type,Binary(RShift(type),tmp,Lit(type2,<size>)))),
			Assign(Bool, <cf>, Binary(And(Bool),Binary(NotEq(type),high,Lit(type2,0)),Binary(NotEq(type),high,Lit(type2,-1)))),
			Assign(Bool, <of>, Binary(And(Bool),Binary(NotEq(type),high,Lit(type2,0)),Binary(NotEq(type),high,Lit(type2,-1))))
		]
	where
		type := SWord(size) ;
		type2 := SWord(arith.MulInt(size,!2)) ;
		tmp := temp

AsmIMUL23(size,dst,src1,src2) =
		![
			Assign(type2, tmp, Binary(Mult(type2),Cast(type2,<src1>),Cast(type2,<src2>))),
			Assign(type, <dst>, Binary(Mult(type),<src1>,<src2>)),
			Assign(Bool, <cf>, Binary(NotEq(type2),tmp,Cast(type2,<dst>))),
			Assign(Bool, <of>, Binary(NotEq(type2),tmp,Cast(type2,<dst>)))
		]
	where
		type := SWord(size) ;
		type2 := SWord(arith.MulInt(size,!2)) ;
		tmp := temp

AsmIMUL(size) =
	[op1] -> <AsmIMUL1(size,!op1)> |
	[op1,op2] -> <AsmIMUL23(size,!op1,!op1,!op2)> |
	[op1,op2,op3] -> <AsmIMUL23(size,!op1,!op2,!op3)>

asmIMULB = AsmIMUL(!8)
asmIMULW = AsmIMUL(!16)
asmIMULL = AsmIMUL(!32)

# FIXME: handle 8 bit specially


AsmDIV(size) =
		[src] -> <
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp1,
				Binary(And(type2),
					Cast(type2,low),
					Binary(LShift(type2),Cast(type2,high),Lit(type2,<size>))
				)
			),
			Assign(type, tmp2, src),
			Assign(type, low, Cast(type,Binary(Div(type2),tmp1,Cast(type2,tmp2)))),
			Assign(type, high, Cast(type,Binary(Mod(type2),tmp1,Cast(type2,tmp2))))
			# FIXME: undefine flags
		]>
	where
		type := Word(size) ;
		type2 := Word(arith.MulInt(size,!2)) ;
		tmp1 := temp ;
		tmp2 := temp

asmDIVB = AsmDIV(!8)
asmDIVW = AsmDIV(!16)
asmDIVL = AsmDIV(!32)


AsmIDIV(size) =
		[src] -> <
		HighLow(size); ?[high,low] ;
		![
			Assign(type2, tmp1,
				Binary(And(type2),
					Cast(type2,low),
					Binary(LShift(type2),Cast(type2,high),Lit(type2,<size>))
				)
			),
			Assign(type, tmp2, src),
			Assign(type, low, Cast(type,Binary(Div(type2),tmp1,Cast(type2,tmp2)))),
			Assign(type, high, Cast(type,Binary(Mod(type2),tmp1,Cast(type2,tmp2))))
			# FIXME: undefine flags
		]>
	where
		type := SWord(size) ;
		type2 := SWord(arith.MulInt(size,!2)) ;
		tmp1 := temp ;
		tmp2 := temp

asmIDIVB = AsmIDIV(!8)
asmIDIVW = AsmIDIV(!16)
asmIDIVL = AsmIDIV(!32)


AsmNEG(size) =
		[dst] -> [
			Assign(type, tmp, dst),
			Assign(type, dst, Unary(Neg(type), dst)),
			*<SubFlags(size, !Lit(type,0), !tmp, !dst)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmNEGB = AsmNEG(!8)
asmNEGW = AsmNEG(!16)
asmNEGL = AsmNEG(!32)


AsmCmp(size) =
		[dst, src] -> [
			Assign(type, tmp, Binary(Minus(type), dst, src)),
			*<SubFlags(size, !dst, !src, !tmp)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmCMPB = AsmCmp(!8)
asmCMPW = AsmCmp(!16)
asmCMPL = AsmCmp(!32)

''')


