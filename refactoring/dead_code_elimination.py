"""Dead code elimination"""


from transf import parse

import ir.sym


parse.Transfs(r'''

#######################################################################
# Needed/uneeded table

shared needed as table

setUnneededVar = needed.unset

setNeededVar = Where(needed.set [<id>,<id>])

setNeededVars =
	#debug.Log(`'Finding needed vars in %s\n'`, id) ;
	traverse.AllTD(
		?Sym(_) ;
		# debug.Log(`'Found var needed %s\n'`, id) ;
		setNeededVar
	)

setAllUnneededVars = needed.clear

setAllNeededVars = needed.Add(ir.sym.local)

isVarNeeded =
	?Sym(_) ;
	(?needed + Not(ir.sym.isLocalVar))


#######################################################################
# Labels

shared label_needed as table

getLabelNeeded =
	Where(
		?GoTo(Sym(label)) &
			!label_needed ;
			Map(Try(?[label,<setNeededVar>])) +
		setAllNeededVars
	)

setLabelNeeded =
	Where(
		?Label(label) ;
		!needed ;
		Map(label_needed.set [label, <id>])
	)


#######################################################################
# Statements

dceAssign =
	with x in
		?Assign(_, x, _) ;
		if ir.sym.isLocalVar x then
			if isVarNeeded x then
				#debug.Log(`'******* var needed %s\n'`, !x) ;
				Where( setUnneededVar x );
				~Assign(_, _, <setNeededVars>)
			else
				#debug.Log(`'******* var uneeded %s\n'`, !x) ;
				!NoStmt
			end
		else
			#debug.Log(`'******* var not local %s\n'`, !x) ;
			~Assign(_, <setNeededVars>, <setNeededVars>)
		end
	end

dceAsm =
	?Asm ;
	setAllNeededVars

dceLabel =
	?Label ;
	setLabelNeeded

dceGoTo =
	?GoTo ;
	getLabelNeeded

dceRet =
	?Ret ;
	setAllUnneededVars ;
	~Ret(_, <setNeededVars>)

elimBlock =
	Block([]) -> NoStmt |
	Block([stmt]) -> stmt

dceBlock =
	~Block(<dceStmts>) ;
	Try(elimBlock)

elimIf =
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)

dceIf =
	~If(_, <dceStmt>, _) \needed/ ~If(_, _, <dceStmt>) ;
	~If(<setNeededVars>, _, _) ;
	Try(elimIf)

elimWhile =
	While(cond,NoStmt) -> Assign(Void,NoExpr,cond)

dceWhile =
	\needed/* ~While(<setNeededVars>, <dceStmt>) ;
	Try(elimWhile)

elimDoWhile =
	DoWhile(cond,NoStmt) -> Assign(Void,NoExpr,cond)

dceDoWhile =
	~DoWhile(<setNeededVars>, _) ;
	\needed/* ~DoWhile(_, <dceStmt>) ;
	Try(elimDoWhile)

dceFunction =
	ir.sym.EnterFunction(
		with label_needed in
			~Function(_, _, _, <
				\label_needed/* with needed in dceStmts end
			>)
		end
	)

# If none of the above applies, assume all vars are needed
dceDefault =
	setAllNeededVars

dceStmt =
	?Assign & dceAssign +
	?Asm & dceAsm +
	?Label & dceLabel +
	?GoTo & dceGoTo +
	?Ret & dceRet +
	?Block & dceBlock +
	?If & dceIf +
	?While & dceWhile +
	?DoWhile & dceDoWhile +
	?Function & dceFunction +
	?Var & id +
	?NoStmt

dceStmts =
	MapR(dceStmt) ;
	Filter(Not(?NoStmt))

dceModule =
	ir.sym.EnterModule(
		with needed, label_needed in
			~Module(<dceStmts>)
		end
	)

dce = dceModule


#######################################################################
# Refactoring

applicable = id

input = ![]

apply =	[root, []] -> root ; dce


#######################################################################
# Tests

testNoStmt =
	!Module([NoStmt]) ;
	dce ;
	?Module([])

testAssign = debug.TestCase(
	!Module([
		Function(Int(32,Signed),"f",[],[
			Assign(Int(32,Signed),Sym("ebx"){Reg},Lit(Int(32,Signed),1)),
			Ret(Int(32,Signed),Sym("eax"){Reg})
		])
	]) ,
	dce ,
	!Module([
		 Function(Int(32,Signed),"f",[],[
			Ret(Int(32,Signed),Sym("eax"){Reg})
		])
	])
)

''')
