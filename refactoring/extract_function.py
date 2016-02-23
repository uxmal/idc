"""Extract Function"""


from transf import parse
import ir.path


parse.Transfs('''

applicable =
	ir.path.Applicable(
		~Module(<
			lists.One(ir.path.isSelected ; ?Label(_) )
		>)
	)

input =
	ir.path.Input2(
		ir.path.projectSelection => Label(label) ;
		![label]
	)

apply =
	[root, [label]] -> root ;
	~Module(<AtSuffix(
		{rest:
			~[Label(?label), *<AtSuffix(
				~[Ret(_,_), *<?rest ; ![]>]
			)>] ;
			![Function(Void, label, [], <project.tail>), *rest]
		}
	)>)


testApply =
	!Module([
		Asm("pre",[]),
		Label("main"),
		Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
		Ret(Int(32,Signed),Sym("eax")),
		Asm("post",[]),
	]) ;
	apply [<id>, ["main"]] ;
	?Module([
		Asm("pre",[]),
		Function(Void,"main",[],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Int(32,Signed),Sym("eax"))
		]),
		Asm("post",[]),
	])

''')
