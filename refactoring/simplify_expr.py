"""Simplify Expression"""


from transf import parse
import ir.match
import ir.path


parse.Transfs(r'''

simplify =
	Binary(Eq(t),Binary(Minus(t),x,y),Lit(t,0))
		-> Binary(Eq(t),x,y) |
	Unary(Not(Bool),Binary(Eq(t),x,y))
		-> Binary(NotEq(t),x,y) |
	Binary(And(_),x,x)
		-> x

applicable =
	ir.path.Applicable(
		ir.path.projectSelection ;
		ir.match.expr ;
		OnceTD(simplify)
	)

input =
	ir.path.Input(
		![]
	)

apply =
	ir.path.Apply(
		[root,[]] -> root ;
		OnceTD(
			ir.path.isSelected ;
			InnerMost(simplify)
		)
	)


testAnd =
	simplify Binary(And(Int(32,Signed)),Sym("x"),Sym("x")) => Sym("x")

''')
