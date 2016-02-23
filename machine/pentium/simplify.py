'''Simplification.'''


from transf import parse
from machine.pentium.common import *


parse.Transfs('''


simplifyExpr =
	Not(Int(1,_)) -> Not(Bool)
|	Or(Int(1,_)) -> Or(Bool)
|	And(Int(1,_)) -> And(Bool)


simplifyStmt =
	Assign(type, dst, Cond(cond, src, dst))
		-> If(cond, Assign(type, dst, src), NoStmt)

|	Assign(type, dst, Cond(cond, src, dst))
		-> If(Unary(Not, cond), Assign(type, dst, src), NoStmt)

|	Assign(_, Sym("pc"), expr)
		-> GoTo(Addr(expr))

|	Cond(cond,Lit(Int(_,_),1),Lit(Int(_,_),0))
		-> cond
|	Cond(cond,Lit(Int(_,_),0),Lit(Int(_,_),1))
		-> Not(cond)

|	Ref(Addr(expr))
		-> expr
|	Addr(Ref(expr))
		-> expr


simplify =
	traverse.InnerMost(
		simplifyExpr +
		simplifyStmt
	)


''')



