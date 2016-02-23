'''Registers.'''


from transf import parse


parse.Transfs('''

Reg(reg) = !Sym(<reg>){Reg}

eax = Reg(!"eax")
ebx = Reg(!"ebx")
ecx = Reg(!"ecx")
edx = Reg(!"edx")
esi = Reg(!"esi")
edi = Reg(!"edi")
ebp = Reg(!"ebp")
esp = Reg(!"esp")

ax = Reg(!"ax")
bx = Reg(!"bx")
cx = Reg(!"cx")
dx = Reg(!"dx")
si = Reg(!"si")
di = Reg(!"di")
bp = Reg(!"bp")
sp = Reg(!"sp")

ah = Reg(!"ah")
bh = Reg(!"bh")
ch = Reg(!"ch")
dh = Reg(!"dh")
al = Reg(!"al")
bl = Reg(!"bl")
cl = Reg(!"cl")
dl = Reg(!"dl")

af = Reg(!"af")
cf = Reg(!"cf")
sf = Reg(!"sf")
of = Reg(!"of")
pf = Reg(!"pf")
zf = Reg(!"zf")
df = Reg(!"df")
if_ = Reg(!"if")

''')

