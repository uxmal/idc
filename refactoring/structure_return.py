"""Structure Return"""


import refactoring
from refactoring.dead_label_elimination import dle

from transf import parse
import ir.path


parse.Transfs('''

Goto(label) =
	ir.path.inSelection ;
	?GoTo(Sym(label))

doReturn =
	with label, rest in
		Where(
			ir.path.projectSelection ;
			?GoTo(Sym(label))
		) ;
		OnceTD(
			AtSuffix(
				Where(
					~[Label(label), *<AtSuffix(~[?Ret, *<![]>])>] ;
					Filter(Not(?Label)) ;
					Map(?Assign + ?Ret) ;
					? rest
				)
			)
		) ;
		OnceTD(Goto(label); !Block(rest))
	end


gotoSelected =
	Where(
		ir.path.projectSelection => GoTo(Sym(_))
	)

functionSelected =
	Where(
		ir.path.projectSelection => Function
	)

common = doReturn

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
