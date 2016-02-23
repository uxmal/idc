"""Structure Loop."""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''


Goto(label) =
	ir.path.inSelection ;
	?GoTo(Sym(label))


liftLoop =
		with label, rest in
			~[Label(label), *<AtSuffix(
				?[<Goto(label)>, *rest] ;
				![]
			) ;
			![While(Lit(Bool,1), Block(<id>)), *rest]
			>]
		end


gotoSelected =
	Where(
		ir.path.projectSelection => GoTo(Sym(_))
	)

functionSelected =
	Where(
		ir.path.projectSelection => Function
	)

common = OnceTD(AtSuffix(liftLoop))

applicable =
	ir.path.Applicable(
		gotoSelected ;
		common
	)

input =
	ir.path.Input(
		![]
	)

apply =
	ir.path.Apply(
		[root,[]] -> root ;
		common ;
		dle
	)


testApply =
	!Module([
		Label("next"),
		Assign(Int(32,Signed), Sym("a"), Sym("b")),
		GoTo(Sym("next"))
	]) ;
	ir.path.annotate ;
	apply [<id>, [[2,0]]] ;
	?Module([
		While(Lit(Bool,1),
			Assign(Int(32,Signed), Sym("a"), Sym("b"))
		)
	])

''')
