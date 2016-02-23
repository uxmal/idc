'''Control Flow Graph (CFG) generation.'''


import aterm
import transf
import box

from transf import util
from transf import lib
from transf import parse

import ir.pprint
import dot


renderBox = (
	util.Adaptor(lambda term: term.factory.makeStr(box.stringify(term))) +
	lib.build.Str("???")
)

parse.Transfs(r'''

#######################################################################
# Graph Generation

shared stmtid

shared this
shared next
shared retn
shared brek
shared cont

shared nodes


getNodeId =
	Label(label) -> label & box.escape +
	Count()

makeNodeLabel =
	( If(cond,_,_)
		-> <ir.pprint.ppExpr cond>
	| While(cond,_)
		-> <ir.pprint.ppExpr cond>
	| DoWhile(cond,_)
		-> <ir.pprint.ppExpr cond>
	| _
		-> <ir.pprint.stmtKern>
	| n(*)
		-> n
	) ;
	renderBox ;
	box.escape

makeNodeShape =
	If
		-> "diamond"
|	While
		-> "diamond"
|	DoWhile
		-> "diamond"
|	Module
		-> "point"
|	Block
		-> "point"
|	NoStmt
		-> "point"
|	_
		-> "box"


makeNodeUrl =
	(path.get & box.reprz + !"" ) ;
	box.escape

makeNodeAttrs =
	![
		!Attr("label", <makeNodeLabel>),
		!Attr("shape", <makeNodeShape>),
		!Attr("URL", <makeNodeUrl>)
	]

MakeEdge(dst) =
	!Edge(<dst>, [])
MakeLabelledEdge(dst, label) =
	!Edge(<dst>, [Attr("label", <label ; box.escape>)])

AddNode(nodeid, attrs, edges) =
	Where(
		!Node(
			<nodeid>,
			<attrs>,
			<edges>
		) ;
		nodes := ![_,*nodes]
	)

GetTerminalNodeId(nodeid) =
	NegInt(nodeid)

hasTerminalNode =
	?Function

addTerminalNode =
	AddNode(
		!retn,
		![
			Attr("label", "\"\""),
			Attr("shape", "doublecircle"),
			Attr("style", "filled"),
			Attr("fillcolor", "black")
		],
		![]
	)


#######################################################################
# Flow Traversal

doStmts =
	MapR(doStmt)

MakeNode(edges) =
	AddNode(!this, makeNodeAttrs, edges)

doDefault =
	MakeNode(![<MakeEdge(!next)>]) ;
	next := !this

doIf =
	with true, false, oldnext in
		oldnext := !next ;
		?If(_,
			<with next in next := !oldnext; doStmt; true := !next end>,
			<with next in next := !oldnext; doStmt; false := !next end>
		) ;
		MakeNode(![
			<MakeLabelledEdge(!true, !"True")>,
			<MakeLabelledEdge(!false, !"False")>,
		]) ;
		next := !this
	end

doNoStmt =
	id

doWhile =
	with true in
		?While(_, <with next in next := !this; doStmt; true := !next end> );
		MakeNode(![
			<MakeLabelledEdge(!true, !"True")>,
			<MakeLabelledEdge(!next, !"False")>,
		]) ;
		next := !this
	end


doDoWhile =
	with false in
		false := !next ;
		next := !this ;
		?DoWhile(_, <doStmt> );
		MakeNode(![
			<MakeLabelledEdge(!next, !"True")>,
			<MakeLabelledEdge(!false, !"False")>,
		])
	end

doBreak =
	MakeNode(![<MakeEdge(!brek)>]) ;
	next := !this

doContinue =
	MakeNode(![<MakeEdge(!cont)>]) ;
	next := !this

doRet =
	MakeNode(![<MakeEdge(!retn)>]) ;
	next := !this

doGoTo =
	with
		label
	in
		?GoTo(Sym(label)) &
		MakeNode(![<MakeEdge(!label ; box.escape)>]) +
		MakeNode(![])
	end ;
	next := !this

doBlock =
	?Block(<doStmts>)

doFunction =
	oldnext := !next ;
	with next, retn, brek, cont in
		next := !oldnext ;
		retn := GetTerminalNodeId(!this) ;
		brek := !0 ;
		cont := !0 ;
		?Function(_, _, _, <doStmts>) ;
		MakeNode(![<MakeEdge(!next)>]) ;
		addTerminalNode
	end

doModule =
	with next, retn, brek, cont in
		next := !0 ;
		retn := !0 ;
		brek := !0 ;
		cont := !0 ;
		?Module(<doStmts>) ;
		addTerminalNode
	end

doStmt =
	with this in
		this := getNodeId ;
		switch project.name
		case "If": doIf
		case "While": doWhile
		case "DoWhile":	doDoWhile
		case "Break": doBreak
		case "GoTo": doGoTo
		case "Continue": doContinue
		case "NoStmt": doNoStmt
		case "Ret": doRet
		case "Block": doBlock
		case "Function": doFunction
		case "Module": doModule
		else doDefault
		end
	end

makeGraph =
	with nodes, stmtid in
		nodes := ![] ;
		stmtid := !0 ;
		doModule ;
		AddNode(!"edge",![Attr("fontname","Arial")],![]) ;
		AddNode(!"node",![Attr("fontname","Arial")],![]) ;
		!Graph(nodes)
	end


#######################################################################
# Graph Simplification

shared point as table

matchPointShapeAttr =
	?Attr("shape", "point")

findPointNode =
	?Node(src, <One(matchPointShapeAttr)>, [Edge(dst, _)]) ;
	point.set [src, dst]

findPointNodes =
	Map(Try(findPointNode))

replaceEdge =
	~Edge(<~point>, _)

removePointNode =
	~Node(<Not(?point)>, _, <Map(Try(replaceEdge))>)

removePointNodes =
	Filter(removePointNode)

simplifyPoints =
	with point in
		~Graph(<findPointNodes; removePointNodes>)
	end

simplifyGraph = simplifyPoints


#######################################################################

render = makeGraph ; simplifyGraph


''')


#######################################################################
# Example


def main():
	import aterm.factory
	import sys
	factory = aterm.factory.factory
	for arg in sys.argv[1:]:
		sys.stderr.write("* Reading aterm\n")
		term = factory.readFromTextFile(file(arg, 'rt'))
		#print ( ir.pprint.module * renderBox )(term)
		#print term
		#print

		sys.stderr.write("* Making Graph\n")
		term = makeGraph(term)
		#print term
		#print

		sys.stderr.write("* Simplifying Graph\n")
		term = simplifyGraph (term)
		#print term
		#print

		sys.stderr.write("* Generating DOT\n")
		term = simplifyGraph (term)
		dotcode = dot.stringify(term)
		sys.stdout.write(dotcode)


if __name__ == '__main__':
	main()
