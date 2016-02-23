"""Inline Temp"""


from transf import parse

import ir.path
import ir.sym


parse.Transfs('''


#######################################################################
# Inline (var, expr) table

shared inline as table

assignInlineVar =
	?[var, expr] ;
	# clobber all expressions containing this variable from the table
	inline.Filter(?[_, <Not(OnceTD(?var))>]) ;
	# update the table
	inline.set [var, expr]

clearInlineVar =
	Try(inline.unset)

clearAllInlineVars =
	inline.clear

inlineVars =
	# expand inline all variables in the table
	AllTD(?Sym; ~inline)


#######################################################################
# Labels' state

shared label_inline as table

setLabelInline =
	Where(
		?GoTo(Sym(label))
		& inline.Filter( ?[var, expr] ; Where(label_inline.set [label,var,expr]) )
		+ id # FIXME
	)

getLabelInline =
	Where(
		?Label(label) ;
		label_inline.Filter( Where(?[label,var,expr]; id /inline\ assignInlineVar [var,expr] ) )
	)


#######################################################################
# Statements

propStmts =
	Map(propStmt) ;
	Filter(Not(?NoStmt))

propAssign =
	~Assign(_, x, < inlineVars ; ?y >) ;
	if ir.path.isSelected then
		assignInlineVar[x, y] ;
		!NoStmt
	else
		Where(clearInlineVar x)
	end

propAsm =
	?Asm ;
	clearAllInlineVars

propLabel =
	?Label ;
	getLabelInline

propGoTo =
	~GoTo(<inlineVars>) ;
	setLabelInline

propRet =
	~Ret(_, <inlineVars>)

propBlock =
	~Block(<propStmts>)

propIf =
	~If(<inlineVars>, _, _) ;
	~If(_, <propStmt>, _) /inline\ ~If(_, _, <propStmt>)

propWhile =
	/inline\* ~While(<inlineVars>, <propStmt>)

propDoWhile =
	/inline\* (
		~DoWhile(_, <propStmt>) ;
		~DoWhile(<inlineVars>, _)
	)

propFunction =
	ir.sym.EnterFunction(
		with label_inline in
			~Function(_, _, _, <
				\label_inline/* with inline in propStmts end
			>)
		end
	)

propDefault =
	clearAllInlineVars

propStmt =
	switch project.name
		case "Assign": propAssign
		case "Asm": propAsm
		case "Label": propLabel
		case "GoTo": propGoTo
		case "Block": propBlock
		case "If": propIf
		case "While": propWhile
		case "DoWhile": propDoWhile
		case "Function": propFunction
		case "Ret": propRet
		case "Break", "Continue", "NoStmt": id
	end

propModule =
	ir.sym.EnterModule(
		~Module(<propStmts>)
	)

prop =
	with inline, label_inline in
		propModule
	end


#######################################################################
# Refactoring

applicable =
	ir.path.Applicable(
		ir.path.projectSelection ;
		?Assign(_, Sym(_), _)
		#OnceTD(?Assign(_, Sym(_), _))
	)

input =
	ir.path.Input(
		![]
	)

apply =
	ir.path.Apply(
		[root,[]] -> root ;
		prop
	)


#######################################################################
# Tests

testApply = debug.TestCase(
	!Module([
		Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
		Assign(Int(32,Signed),Sym("ebx"),Sym("eax"))
	]) ;
	ir.path.annotate ,
	apply [_, [[0,0]]] ,
	!Module([
		Assign(Int(32,Signed),Sym("ebx"),Lit(Int(32,Signed),1))
	])
)

''')
