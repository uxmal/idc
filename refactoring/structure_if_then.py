"""Structure If"""


from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''

Goto(label) =
	ir.path.inSelection ;
	?GoTo(Sym(label))

liftIfThen =
		with cond, label, rest in
			~[If(cond, <Goto(label)>, NoStmt), *<AtSuffix(
				?[Label(label), *] ; ?rest ;
				![]
			)>] ;
			![If(Unary(Not(Bool), cond), Block(<project.tail>), NoStmt), *rest]
		end

gotoSelected =
	Where(
		ir.path.projectSelection => GoTo(Sym(_))
	)

functionSelected =
	Where(
		ir.path.projectSelection => Function
	)

common = OnceTD(AtSuffix(liftIfThen))

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
