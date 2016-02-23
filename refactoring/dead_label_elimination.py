"""Dead Label Elimination"""


from transf import parse


parse.Transfs('''


#######################################################################
# Labels

shared needed_label as table

updateNeededLabels =
	Where(
		?GoTo(Sym(label)) ;
		needed_label.set [label,label]
	)

#######################################################################
# Statements

dleLabel =
	Try(
		?Label(<Not(~needed_label)>) ;
		!NoStmt
	)

elimBlock =
	Block([]) -> NoStmt |
	Block([stmt]) -> stmt

dleBlock =
	~Block(<dleStmts>) ;
	Try(elimBlock)

elimIf =
	If(cond,NoStmt,NoStmt) -> Assign(Void,NoExpr,cond) |
	If(cond,NoStmt,false) -> If(Unary(Not,cond),false,NoStmt)

dleIf =
	~If(_, <dleStmt>, <dleStmt>) ;
	Try(elimIf)

elimWhile =
	While(cond,NoStmt) -> Assign(Void,NoExpr,cond)

dleWhile =
	~While(_, <dleStmt>) ;
	Try(elimWhile)

elimDoWhile =
	DoWhile(cond,NoStmt) -> Assign(Void,NoExpr,cond)

dleDoWhile =
	~DoWhile(_, <dleStmt>) ;
	Try(elimDoWhile)

dleFunction =
	{needed_label:
		AllTD(updateNeededLabels) ;
		~Function(_, _, _, <dleStmts>)
	}

# If none of the above applies, assume all vars are needed
dleDefault =
	id

dleStmt =
	?Label & dleLabel +
	?Block & dleBlock +
	?If & dleIf +
	?While & dleWhile +
	?DoWhile & dleDoWhile +
	?Function & dleFunction +
	id

dleStmts =
	MapR(dleStmt) ;
	Filter(Not(?NoStmt))

dleModule =
	~Module(<dleStmts>)

dle =
	{needed_label:
		AllTD(updateNeededLabels) ;
		dleModule
	}


testUnusedLabel =
    !Module([
    	Label("A")
    ]) ;
    dle ;
    ?Module([])

testUsedLabel =
    !Module([
    	GoTo(Sym("A")),
    	Label("A")
    ]) ;
    dle ;
    ?Module([
    	GoTo(Sym("A")),
    	Label("A")
    ])

''')
