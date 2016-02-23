''' arithmetic instructions.'''


from transf import parse
from machine.pentium.common import *
from machine.pentium.data import *


parse.Transfs('''


asmSTC = [] -> [Assign(Bool, <cf>, Lit(Bool,1))]
asmCLC = [] -> [Assign(Bool, <cf>, Lit(Bool,0))]
asmCMC = [] -> [Assign(Bool, <cf>, Unary(Not(Bool),<cf>))]


asmSTD = [] -> [Assign(Bool, <df>, Lit(Bool,1))]
asmCLD = [] -> [Assign(Bool, <df>, Lit(Bool,0))]


asmLAHF = [] -> [
		Assign(type, <ah>,
			Binary(Or(type), Cond(<cf>, Lit(type,0x01), Lit(type,0)),
			Binary(Or(type), Lit(type,0x02),
			Binary(Or(type), Cond(<pf>, Lit(type,0x04), Lit(type,0)),
			Binary(Or(type), Cond(<af>, Lit(type,0x10), Lit(type,0)),
			Binary(Or(type), Cond(<zf>, Lit(type,0x40), Lit(type,0)),
				Cond(<sf>, Lit(type,0x80), Lit(type,0))
		))))))
	] where
		type := UWord(!8)


asmSAHF = [] -> [
		Assign(type, <cf>, Binary(And(type), <ah>, Lit(type,0x01))),
		Assign(type, <pf>, Binary(And(type), <ah>, Lit(type,0x04))),
		Assign(type, <af>, Binary(And(type), <ah>, Lit(type,0x10))),
		Assign(type, <zf>, Binary(And(type), <ah>, Lit(type,0x40))),
		Assign(type, <sf>, Binary(And(type), <ah>, Lit(type,0x80)))
	] where
		type := UWord(!8)


asmPUSHFL = [] -> [
		Binary(Or(type), Cond(<cf>, Lit(type,0x01), Lit(type,0)),
		Binary(Or(type), Lit(type,0x02),
		Binary(Or(type), Cond(<pf>, Lit(type,0x04), Lit(type,0)),
		Binary(Or(type), Cond(<af>, Lit(type,0x10), Lit(type,0)),
		Binary(Or(type), Cond(<zf>, Lit(type,0x40), Lit(type,0)),
			Cond(<sf>, Lit(type,0x80), Lit(type,0)))))))
		# FIXME: incomplete
	] ; asmPUSHL
		where type := UWord(!32)


asmPOPFL = [] -> [
		<asmPOPL [tmp] >,
		Assign(type, <cf>, Binary(And(type), tmp, Lit(type,0x01))),
		Assign(type, <pf>, Binary(And(type), tmp, Lit(type,0x04))),
		Assign(type, <af>, Binary(And(type), tmp, Lit(type,0x10))),
		Assign(type, <zf>, Binary(And(type), tmp, Lit(type,0x40))),
		Assign(type, <sf>, Binary(And(type), tmp, Lit(type,0x80)))
		# FIXME: incomplete
	] where
		type := UWord(!32) ;
		tmp := temp


asmSTI = [] -> [Assign(Bool, <if_>, Lit(Bool,1))]
asmCLI = [] -> [Assign(Bool, <if_>, Lit(Bool,0))]


''')
