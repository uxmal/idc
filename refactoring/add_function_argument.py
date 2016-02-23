"""Add Function Argument"""


from transf import parse
import ir.path

parse.Transfs('''

applicable =
	ir.path.Applicable(
		ir.path.projectSelection => Function(_, _, _, _)
	)

input =
	ir.path.Input2(
		ir.path.projectSelection => Function(_, name, _, _) ;
		ui.Str(!"Add Function Argument", !"Argument Symbol?") => arg ;
		![name, arg]
	)

apply =
	[root, [name, arg]] -> root ;
	type := !Int(32,Signed) ;
	~Module(<
		One(
			~Function(_, ?name, <Concat(id,![Arg(type,arg)])>, _)
		)
	>) ;
	BottomUp(Try(
		~Call(Sym(?name), <Concat(id,![Sym(arg)])>)
	))

testApply =
	![
		Module([
			Function(Void,"main",[],[
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Void,NoExpr)
			]),
		]),
		["main", "eax"]
	] ;
	apply ;
	?Module([
		Function(Void,"main",[Arg(Int(32,Signed),"eax")],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Void,NoExpr)
		]),
	])

''')