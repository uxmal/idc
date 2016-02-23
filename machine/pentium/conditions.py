'''Condition codes.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''


# Equality conditions

ccZ = zf
ccNZ = LNot(zf)
ccE = ccZ
ccNE = ccNZ

ccCXZ  = LNot(cx)
ccECXZ = LNot(ecx)


# Unsigned conditions

ccA = LAnd(LNot(cf),LNot(zf))
ccAE = LNot(cf)
ccB = cf
ccBE = LOr(cf, zf)

ccNBE = ccA
ccNB = ccNC
ccNAE = ccB
ccNA = ccBE

ccC = cf
ccNC = LNot(cf)


# Signed conditions

ccG   = LOr(LNotEq(sf,of),LNot(zf))
ccGE  = LNotEq(sf,of)
ccL   = LEq(sf,of)
ccLE  = LOr(LEq(sf,of),zf)

ccNLE = ccG
ccNL  = ccGE
ccNGE = ccL
ccNG  = ccLE

ccO = of
ccNO = LNot(of)

ccS = sf
ccNS = LNot(sf)


# Miscellaneous

ccP = pf
ccNP = LNot(pf)
ccPE = ccP
ccPO = ccNP


''')
