"""Structure Continue"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''

liftContinue =
	~[Label(label), <
		~While(_, < OnceTD( (GoTo(Sym(label)) -> Continue if ir.path.inSelection) ) >) +
		~DoWhile(_, < OnceTD( (GoTo(Sym(label)) -> Continue if ir.path.inSelection) ) >)
	>, *]


gotoSelected =
	Where(
		ir.path.projectSelection => GoTo(Sym(_))
	)

functionSelected =
	Where(
		ir.path.projectSelection => Function
	)

common =
	OnceTD(AtSuffix(liftContinue))

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


xtestApply =
	!Module([
		Label("continue"),
		While(Lit(Bool,1), Block([
			Assign(Int(32,Signed), Sym("a"), Sym("b")),
			GoTo(Sym("continue"))
		]))
	]) ;
	ir.path.annotate ;
	apply [<id>, [[0,1,1,0,1]]] ;
	?Module([
		While(Lit(Bool,1), Block([
			Assign(Int(32,Signed), Sym("a"), Sym("b")),
			Continue
		]))
	])

''')
