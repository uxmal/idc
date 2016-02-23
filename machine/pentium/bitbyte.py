'''Bit and byte instructions.'''


from transf import parse
from machine.pentium.common import *
from machine.pentium.conditions import *
from machine.pentium.logical import LogFlags


parse.Transfs('''

BitMask(size, offset) =
	!Binary(LShift(type), Lit(type,1),
		Binary(Mod(type), <offset>, Lit(type,<size>)))
	where
		type := Word(size)

Bit(size, base, offset) =
	!Binary(And(type), <base>, <BitMask(size, offset)>)
	where
		type := Word(size)


AsmBT(size) =
	[dst, src] -> [Assign(Bool,<cf>,<Bit(size,!dst,!src)>)]

asmBTW = AsmBT(!16)
asmBTL = AsmBT(!32)


AsmBTS(size) =
	[dst, src] -> [
		Assign(Bool,<cf>,<Bit(size,!dst,!src)>),
		Assign(type,dst,Binary(Or(type),dst,<BitMask(size,!src)>))
	] where
		type := Word(size)

asmBTSW = AsmBTS(!16)
asmBTSL = AsmBTS(!32)


AsmBTR(size) =
	[dst, src] -> [
		Assign(Bool,<cf>,<Bit(size,!dst,!src)>),
		Assign(type,dst,
			Binary(And(type),dst,
				Unary(Not(type),<BitMask(size,!src)>)))
	] where
		type := Word(size)

asmBTRW = AsmBTR(!16)
asmBTRL = AsmBTR(!32)


AsmBTC(size) =
	[dst, src] -> [
		Assign(Bool,<cf>,<Bit(size,!dst,!src)>),
		Assign(type,dst,Binary(Xor(type),dst,<BitMask(size,!src)>))
	] where
		type := Word(size)

asmBTCW = AsmBTC(!16)
asmBTCL = AsmBTC(!32)


AsmBS(size, builtin) =
	[dst, src] -> [
		Assign(Bool, <zf>, Binary(Eq(type), src, Lit(type,0))),
		Assign(type, dst, Call(Sym(<builtin>){Builtin},[src])),
	] where
		type := Word(size)

AsmBSF(size) = AsmBS(size, !"_bit_scan_reverse")
AsmBSR(size) = AsmBS(size, !"_bit_scan_forward")

asmBSFW = AsmBSF(!16)
asmBSFL = AsmBSF(!32)

asmBSRW = AsmBSR(!16)
asmBSRL = AsmBSR(!32)


AsmSETcc(cc) =
	[dst] -> [
		Assign(type, dst, Cond(<cc>, Lit(type,1), Lit(type,0)))
	] where
		type := Word(!8)

asmSETA   = AsmSETcc(ccA  )
asmSETAE  = AsmSETcc(ccAE )
asmSETB   = AsmSETcc(ccB  )
asmSETBE  = AsmSETcc(ccBE )
asmSETC   = AsmSETcc(ccC  )
asmSETE   = AsmSETcc(ccE  )
asmSETG   = AsmSETcc(ccG  )
asmSETGE  = AsmSETcc(ccGE )
asmSETL   = AsmSETcc(ccL  )
asmSETLE  = AsmSETcc(ccLE )
asmSETNA  = AsmSETcc(ccNA )
asmSETNAE = AsmSETcc(ccNAE)
asmSETNB  = AsmSETcc(ccNB )
asmSETNBE = AsmSETcc(ccNBE)
asmSETNC  = AsmSETcc(ccNC )
asmSETNE  = AsmSETcc(ccNE )
asmSETNG  = AsmSETcc(ccNG )
asmSETNGE = AsmSETcc(ccNGE)
asmSETNL  = AsmSETcc(ccNL )
asmSETNLE = AsmSETcc(ccNLE)
asmSETNO  = AsmSETcc(ccNO )
asmSETNP  = AsmSETcc(ccNP )
asmSETNS  = AsmSETcc(ccNS )
asmSETNZ  = AsmSETcc(ccNZ )
asmSETO   = AsmSETcc(ccO  )
asmSETP   = AsmSETcc(ccP  )
asmSETPE  = AsmSETcc(ccPE )
asmSETPO  = AsmSETcc(ccPO )
asmSETS   = AsmSETcc(ccS  )
asmSETZ   = AsmSETcc(ccZ  )


AsmTEST(size) =
	[dst, src] -> [
		Assign(type, tmp, Binary(And(type), dst, src)),
		*<LogFlags(size, !tmp)>
	]
	where
		type := Word(size) ;
		tmp := temp

asmTESTB = AsmTEST(!8)
asmTESTW = AsmTEST(!16)
asmTESTL = AsmTEST(!32)


''')

