'''Data transfer instructions.'''


from transf import parse
from machine.pentium.common import *
from machine.pentium.conditions import *
from machine.pentium.binary import *

parse.Transfs('''

AsmMOV(size) =
	[dst,src] -> [Assign(<Word(size)>,dst,src)]

asmMOVB = AsmMOV(!8)
asmMOVW = AsmMOV(!16)
asmMOVL = AsmMOV(!32)


AsmCMOVcc(size,cond) =
	[dst,src] -> [If(<cond>,Assign(<Word(size)>,dst,src),NoStmt)]

asmCMOVAW   = AsmCMOVcc(!16, ccA   )
asmCMOVAEW  = AsmCMOVcc(!16, ccAE  )
asmCMOVBW   = AsmCMOVcc(!16, ccB   )
asmCMOVBEW  = AsmCMOVcc(!16, ccBE  )
asmCMOVCW   = AsmCMOVcc(!16, ccC   )
asmCMOVEW   = AsmCMOVcc(!16, ccE   )
asmCMOVGW   = AsmCMOVcc(!16, ccG   )
asmCMOVGEW  = AsmCMOVcc(!16, ccGE  )
asmCMOVLW   = AsmCMOVcc(!16, ccL   )
asmCMOVLEW  = AsmCMOVcc(!16, ccLE  )
asmCMOVNAW  = AsmCMOVcc(!16, ccNA  )
asmCMOVNAEW = AsmCMOVcc(!16, ccNAE )
asmCMOVNBW  = AsmCMOVcc(!16, ccNB  )
asmCMOVNBEW = AsmCMOVcc(!16, ccNBE )
asmCMOVNCW  = AsmCMOVcc(!16, ccNC  )
asmCMOVNEW  = AsmCMOVcc(!16, ccNE  )
asmCMOVNGW  = AsmCMOVcc(!16, ccNG  )
asmCMOVNGEW = AsmCMOVcc(!16, ccNGE )
asmCMOVNLW  = AsmCMOVcc(!16, ccNL  )
asmCMOVNLEW = AsmCMOVcc(!16, ccNLE )
asmCMOVNOW  = AsmCMOVcc(!16, ccNO  )
asmCMOVNPW  = AsmCMOVcc(!16, ccNP  )
asmCMOVNSW  = AsmCMOVcc(!16, ccNS  )
asmCMOVNZW  = AsmCMOVcc(!16, ccNZ  )
asmCMOVOW   = AsmCMOVcc(!16, ccO   )
asmCMOVPW   = AsmCMOVcc(!16, ccP   )
asmCMOVPEW  = AsmCMOVcc(!16, ccPE  )
asmCMOVPOW  = AsmCMOVcc(!16, ccPO  )
asmCMOVSW   = AsmCMOVcc(!16, ccS   )
asmCMOVZW   = AsmCMOVcc(!16, ccZ   )

asmCMOVAL   = AsmCMOVcc(!32, ccA   )
asmCMOVAEL  = AsmCMOVcc(!32, ccAE  )
asmCMOVBL   = AsmCMOVcc(!32, ccB   )
asmCMOVBEL  = AsmCMOVcc(!32, ccBE  )
asmCMOVCL   = AsmCMOVcc(!32, ccC   )
asmCMOVEL   = AsmCMOVcc(!32, ccE   )
asmCMOVGL   = AsmCMOVcc(!32, ccG   )
asmCMOVGEL  = AsmCMOVcc(!32, ccGE  )
asmCMOVLL   = AsmCMOVcc(!32, ccL   )
asmCMOVLEL  = AsmCMOVcc(!32, ccLE  )
asmCMOVNAL  = AsmCMOVcc(!32, ccNA  )
asmCMOVNAEL = AsmCMOVcc(!32, ccNAE )
asmCMOVNBL  = AsmCMOVcc(!32, ccNB  )
asmCMOVNBEL = AsmCMOVcc(!32, ccNBE )
asmCMOVNCL  = AsmCMOVcc(!32, ccNC  )
asmCMOVNEL  = AsmCMOVcc(!32, ccNE  )
asmCMOVNGL  = AsmCMOVcc(!32, ccNG  )
asmCMOVNGEL = AsmCMOVcc(!32, ccNGE )
asmCMOVNLL  = AsmCMOVcc(!32, ccNL  )
asmCMOVNLEL = AsmCMOVcc(!32, ccNLE )
asmCMOVNOL  = AsmCMOVcc(!32, ccNO  )
asmCMOVNPL  = AsmCMOVcc(!32, ccNP  )
asmCMOVNSL  = AsmCMOVcc(!32, ccNS  )
asmCMOVNZL  = AsmCMOVcc(!32, ccNZ  )
asmCMOVOL   = AsmCMOVcc(!32, ccO   )
asmCMOVPL   = AsmCMOVcc(!32, ccP   )
asmCMOVPEL  = AsmCMOVcc(!32, ccPE  )
asmCMOVPOL  = AsmCMOVcc(!32, ccPO  )
asmCMOVSL   = AsmCMOVcc(!32, ccS   )
asmCMOVZL   = AsmCMOVcc(!32, ccZ   )


AsmXCHG(size) =
	[dst,src] -> [
		Assign(type,tmp,dst),
		Assign(type,dst,src),
		Assign(type,src,tmp)
	]
	where
		type := Word(size) ;
		tmp := temp

asmXCHGB = AsmXCHG(!8)
asmXCHGW = AsmXCHG(!16)
asmXCHGL = AsmXCHG(!32)


# FIXME: BSWAP


AsmXADD(size) =
		[dst, src] -> [
			Assign(type, tmp, Binary(Plus(type), dst, src)),
			Assign(type, src, dst),
			Assign(type, dst, tmp),
			*<AddFlags(size, !src, !dst, !tmp)>
		]
	where
		type := Word(size) ;
		tmp := temp

asmXADDB = AsmXADD(!8)
asmXADDW = AsmXADD(!16)
asmXADDL = AsmXADD(!32)


AsmCMPXCHG(size,accum) =
		[dst, src] -> [
			Assign(type, tmp, Binary(Minus(type), <accum>, dst)),
			*<SubFlags(size, accum, !src, !tmp)>,
			If(Binary(Eq(type),<accum>,dst),
				Assign(type, dst, src),
				Assign(type, <accum>, dst)
			)
		]
	where
		type := Word(size) ;
		tmp := temp

asmCMPXCHGB = AsmCMPXCHG(!8,   al)
asmCMPXCHGW = AsmCMPXCHG(!16,  ax)
asmCMPXCHGL = AsmCMPXCHG(!32, eax)


# FIXME: CMPXCHG8B


AsmPUSH(size) =
	[src] -> [
		Assign(type, <esp>, Binary(Minus(type), <esp>, Lit(type,4))),
		Assign(type, Ref(<esp>), src)
	] where
		type := Word(size)

asmPUSHW = AsmPUSH(!16)
asmPUSHL = AsmPUSH(!32)


AsmPOP(size) =
	[dst] -> [
		Assign(type, dst, Ref(<esp>)),
		Assign(type, <esp>, Binary(Plus(type), <esp>, Lit(type,4)))
	] where
		type := Word(size)

asmPOPW = AsmPOP(!16)
asmPOPL = AsmPOP(!32)


asmPUSHAD =
	[] -> [
		Assign(<Word(!32)>, tmp, <esp>),
		*<lists.MapConcat(asmPUSHL [_]) [<eax>, <ecx>, <edx>, <ebx>, tmp , <esi>, <edi>]>
	] where
		tmp := temp

asmPOPAD =
	[] -> [
		*<lists.MapConcat(asmPOPL [_]) [<eax>, <ecx>, <edx>, <ebx>, tmp , <esi>, <edi>]>
	] where
		tmp := temp


AsmIN(size, builtin) =
	[dst, src] -> [Assign(<Word(size)>,dst,Call(Sym(<builtin>){Builtin},[src]))]

asmINB = AsmIN(!8, !"_inp")
asmINW = AsmIN(!8, !"_inpw")
asmINL = AsmIN(!8, !"_inpd")


AsmOUT(size, builtin) =
	[dst, src] -> [Assign(Void,NoExpr,Call(Sym(<builtin>){Builtin},[dst,src]))]

asmOUTB = AsmOUT(!8, !"_outp")
asmOUTW = AsmOUT(!8, !"_outpw")
asmOUTL = AsmOUT(!8, !"_outpd")


asmCWTD =
	[] -> [
		If(Binary(Lt(type),<ax>,Lit(type,0)),
			Assign(type,<dx>,Lit(type,-1)),
			Assign(type,<dx>,Lit(type,0))
		)
	] where
		type := SWord(!16)


asmCLTD =
	[] -> [
		If(Binary(Lt(type),<eax>,Lit(type,0)),
			Assign(type,<edx>,Lit(type,-1)),
			Assign(type,<edx>,Lit(type,0))
		)
	] where
		type := SWord(!32)


AsmMOVSX(size, dst, src) =
	![Assign(Int(<size>,Signed), <dst>, Cast(Int(<size>,Signed),<src>))]

asmCBTW = [] -> <AsmMOVSX(!16,ax,al)>

asmCWTL = [] -> <AsmMOVSX(!16,eax,ax)>

asmMOVSBW = [dst, src] -> <AsmMOVSX(!16, !dst, !src)>
asmMOVSBL = [dst, src] -> <AsmMOVSX(!32, !dst, !src)>
asmMOVSWL = [dst, src] -> <AsmMOVSX(!32, !dst, !src)>


AsmMOVZX(size) =
	[dst, src] -> [Assign(Int(<size>,Unsigned), dst, Cast(Int(<size>,Unsigned),src))]

asmMOVZBW = AsmMOVZX(!16)
asmMOVZBL = AsmMOVZX(!32)
asmMOVZWL = AsmMOVZX(!32)


''')
