'''Miscellaneous instructions.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''


AsmLEA(size) =
	[dst,src] -> [Assign(<Word(size)>,dst,Addr(src))]

asmLEAW = AsmLEA(!8)
asmLEAL = AsmLEA(!16)


asmNOP =
	[] -> [NoStmt]


# FIXME: UD2
# FIXME: XLAT/XLATB
# FIXME: CPUID


''')


