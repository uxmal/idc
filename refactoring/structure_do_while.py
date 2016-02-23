"""Structure Do-While"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''


Goto(label) =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftDoWhile =
		with label, cond, rest in
			~[Label(label), *<AtSuffix(
				?[If(_,<Goto(label)>,NoStmt), *] ;
				?[If(cond,_,_), *rest] ;
				![]
			) ;
			![DoWhile(cond, Block(<id>)), *rest]
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

common = OnceTD(AtSuffix(liftDoWhile))

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
		If(Sym("a"),GoTo(Sym("next")),NoStmt)
	]) ;
	ir.path.annotate ;
	apply [_, [[1,2,0]]] ;
	?Module([
		DoWhile(Sym("a"),
			Assign(Int(32,Signed), Sym("a"), Sym("b"))
		)
	])
''')
