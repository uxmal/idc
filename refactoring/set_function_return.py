"""Set Function Return"""


from transf import parse
import ir.traverse
import ir.path


parse.Transfs('''

applicable =
	ir.path.Applicable(
		ir.path.projectSelection => Function(Void, _, _, _)
	)

input =
	ir.path.Input2(
		ir.path.projectSelection => Function(_, name, _, _) ;
		ui.Str(!"Set Function Return", !"Return Symbol?") => ret ;
		![name, ret]
	)

apply =
		( [root, [name, ret]] -> root ) ;
		~Module(<
			One(
				~Function(!type, ?name, _, <
					AllTD(~Ret(!type, !Sym(ret)))
				>)
			)
		>) ;
		ir.traverse.AllStmtsBU(Try(
			?Assign(Void, NoExpr, Call(Sym(?name), _)) ;
			~Assign(!type, !Sym(ret), _)
		))
	where
		type := !Int(32,Signed)


testApply =
	!Module([
		Function(Void,"main",[],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Void,NoExpr)
		]),
	]) ;
	apply [<id>, ["main","eax"] ] ;
	?Module([
		Function(Int(32,Signed),"main",[],[
			Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
			Ret(Int(32,Signed),Sym("eax"))
		]),
	])

''')
