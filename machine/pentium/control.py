'''Control transfer instructions.'''


from transf import parse
from machine.pentium.common import *
from machine.pentium.conditions import *
from machine.pentium.data import *


parse.Transfs('''

asmJMPL =
	[Ref(addr)] -> [GoTo(addr)]

asmJMP = asmJMPL


AsmJcc(cond) =
	[Ref(addr)] -> [If(<cond>,GoTo(addr),NoStmt)]

asmJA    = AsmJcc(ccA   )
asmJAE   = AsmJcc(ccAE  )
asmJB    = AsmJcc(ccB   )
asmJBE   = AsmJcc(ccBE  )
asmJC    = AsmJcc(ccC   )
asmJCXZ  = AsmJcc(ccCXZ )
asmJECXZ = AsmJcc(ccECXZ)
asmJE    = AsmJcc(ccE   )
asmJG    = AsmJcc(ccG   )
asmJGE   = AsmJcc(ccGE  )
asmJL    = AsmJcc(ccL   )
asmJLE   = AsmJcc(ccLE  )
asmJNA   = AsmJcc(ccNA  )
asmJNAE  = AsmJcc(ccNAE )
asmJNB   = AsmJcc(ccNB  )
asmJNBE  = AsmJcc(ccNBE )
asmJNC   = AsmJcc(ccNC  )
asmJNE   = AsmJcc(ccNE  )
asmJNG   = AsmJcc(ccNG  )
asmJNGE  = AsmJcc(ccNGE )
asmJNL   = AsmJcc(ccNL  )
asmJNLE  = AsmJcc(ccNLE )
asmJNO   = AsmJcc(ccNO  )
asmJNP   = AsmJcc(ccNP  )
asmJNS   = AsmJcc(ccNS  )
asmJNZ   = AsmJcc(ccNZ  )
asmJO    = AsmJcc(ccO   )
asmJP    = AsmJcc(ccP   )
asmJPE   = AsmJcc(ccPE  )
asmJPO   = AsmJcc(ccPO  )
asmJS    = AsmJcc(ccS   )
asmJZ    = AsmJcc(ccZ   )


AsmLOOP(size, counter) =
	[Ref(addr)] -> [
		Assign(type, <counter>, Binary(Minus(type),<counter>, Lit(type,1))),
		If(Binary(Eq(type),<counter>,Lit(type,0)), GoTo(addr), NoStmt)
	] where type := UWord(size)

asmLOOPW = AsmLOOP(!16, cx)
asmLOOPL = AsmLOOP(!16, ecx)


AsmLOOPcc(size, counter, cc) =
	[Ref(addr)] -> [
		Assign(type, <counter>, Binary(Minus(type),<counter>, Lit(type,1))),
		If(Binary(And(Bool), Binary(Eq(type),<counter>,Lit(type,0)), <cc>),
			GoTo(addr),
			NoStmt
		)
	] where type := UWord(size)

asmLOOPEW  = AsmLOOPcc(!16, cx, ccE )
asmLOOPZW  = AsmLOOPcc(!16, cx, ccZ )
asmLOOPNEW = AsmLOOPcc(!16, cx, ccNE)
asmLOOPNZW = AsmLOOPcc(!16, cx, ccNZ)

asmLOOPEL  = AsmLOOPcc(!32, ecx, ccE )
asmLOOPZL  = AsmLOOPcc(!32, ecx, ccZ )
asmLOOPNEL = AsmLOOPcc(!32, ecx, ccNE)
asmLOOPNZL = AsmLOOPcc(!32, ecx, ccNZ)


asmCALLL =
	[Ref(addr)] -> [Assign(Void, NoExpr, Call(addr,[]))]

asmCALL = asmCALLL


asmRETL =
	[] -> [Ret(Void, NoExpr)] |
	[size] -> [Ret(Void, NoExpr)]

asmRET = asmRETL


# FIXME: INT
# FIXME: IRET
# FIXME: INT
# FIXME: INTO

# FIXME: BOUND


# FIXME: deal with level
asmENTERL =
	[size, level] -> [
		*<AsmPUSH(!32) [<ebp>]>,
		Assign(type, <ebp>, <esp>),
		Assign(type, <esp>, Binary(Minus(type), <esp>, size))
	] where type := UWord(!32)

asmENTER = asmENTERL


asmLEAVEL =
	[] -> [
		Assign(type, <esp>, <ebp>),
		*<AsmPOP(!32) [<ebp>]>
	] where type := UWord(!32)

asmLEAVE = asmLEAVEL

''')



