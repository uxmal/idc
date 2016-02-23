"""Structure If-Else"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''


Goto(label) =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftIfElse =
		with
			cond, false_stmts,
			true_label, true_stmts,
			rest_label, rest_stmts
		in
			~[If(cond, <ir.path.inSelection;?GoTo(Sym(true_label))>, NoStmt), *<AtSuffix(
				~[GoTo(Sym(rest_label)), Label(true_label), *<AtSuffix(
					?[Label(rest_label), *] => rest_stmts ;
					![]
				)>] ; project.tail => true_stmts ;
				![]
			)>] ; project.tail => false_stmts ;
			![If(cond, Block(true_stmts), Block(false_stmts)), *rest_stmts]
		end

gotoSelected =
	Where(
		ir.path.projectSelection => GoTo(Sym(_))
	)

functionSelected =
	Where(
		ir.path.projectSelection => Function
	)

common = OnceTD(AtSuffix(liftIfElse))

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

''')
