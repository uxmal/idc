'''Preambule code.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''

reg32Names = ![
	"eax", "ebx", "ecx", "edx",
	"esi", "edi", "ebp", "esp"
]

reg16Names = ![
	"ax", "bx", "cx", "dx",
	"si", "di", "bp", "sp"
]

reg8Names = ![
	"ah", "bh", "ch", "dh",
	"al", "bl", "cl", "dl"
]

flagNames = ![
	"sf", "zf", "af", "pf",
	"cf", "of", "df", "if"
]

declReg32 = !Var(Int(32,NoSign),<id>,NoExpr)
declFlag = !Var(Bool,<id>,NoExpr)

stmtsPreambule =
	Concat(
		reg32Names ; Map(declReg32) ,
		flagNames ; Map(declFlag)
	)

''')


