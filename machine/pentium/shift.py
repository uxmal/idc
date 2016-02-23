'''Shift and rotate instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''

# FIXME: truncate src

_AsmSxL(size, sign, dst, src) =
	![
		Assign(type, tmp, <dst>),
		Assign(type, <dst>, Binary(LShift(type), <dst>, <src>)),
		# FIXME: deal with zero count
		Assign(Bool, <cf>, Binary(And(type), tmp,
			Binary(LShift(type),Lit(type,1),
				Binary(Minus(type),Lit(type,<size>), <src>))
		)),
		Assign(Bool, <of>, <LNotEq(HsbOne(size,dst),cf)>)
	]
	where
		type := !Int(<size>,<sign>) ;
		tmp := temp

AsmSxL(size, sign) =
	[dst] -> <_AsmSxL(size, sign, !dst, !Lit(Int(<size>,<sign>),1))> |
	[dst,src] -> <_AsmSxL(size, sign, !dst, !src)>

asmSHLB = AsmSxL(!8, !Unsigned)
asmSHLW = AsmSxL(!16, !Unsigned)
asmSHLL = AsmSxL(!32, !Unsigned)
asmSALB = AsmSxL(!8, !Signed)
asmSALW = AsmSxL(!16, !Signed)
asmSALL = AsmSxL(!32, !Signed)

_AsmSxR(size, sign, dst, src) =
	![
		Assign(type, tmp, <dst>),
		Assign(type, <dst>, Binary(RShift(type), <dst>, <src>)),
		Assign(Bool, <cf>, Binary(And(type), tmp,
			Binary(RShift(type),Lit(type,1),
				Binary(Minus(type),<src>, Lit(type,1)))
		)),
		Assign(Bool, <of>,
			<switch sign
			case Unsigned:
				!Lit(Bool, 0)
			case Signed:
				HsbOne(size,!tmp)
			end>
		)
	]
	where
		type := !Int(<size>,<sign>) ;
		tmp := temp


AsmSxR(size, sign) =
	[dst] -> <_AsmSxR(size, sign, !dst, !Lit(Int(<size>,<sign>),1))> |
	[dst,src] -> <_AsmSxR(size, sign, !dst, !src)>

asmSHRB = AsmSxR(!8, !Unsigned)
asmSHRW = AsmSxR(!16, !Unsigned)
asmSHRL = AsmSxR(!32, !Unsigned)
asmSARB = AsmSxR(!8, !Signed)
asmSARW = AsmSxR(!16, !Signed)
asmSARL = AsmSxR(!32, !Signed)


# FIXME: SHRD
# FIXME: SHLD

# FIXME: ROR
# FIXME: ROL
# FIXME: RCR
# FIXME: RCL


''')


