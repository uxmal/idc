'''Pretty-printing of intermediate representation code.
'''


import math

from transf import util
from transf.lib import *
from transf import parse

import box
from box import op as ppOp
from box import kw
from box import lit
from box import sym
from box import commas
from box import Path


#######################################################################
# Int Literals

def _entropy(seq, states):
	state_freqs = dict.fromkeys(states, 0)
	for state in seq:
		state_freqs[state] += 1
	entropy = 0
	nstates = len(seq)
	for freq in state_freqs.itervalues():
		prob = float(freq)/nstates
		if prob:
			entropy -= prob*math.log(prob)
	return entropy

@util.Adaptor
def intrepr(term):
	'''Represent integers, choosing the most suitable (lowest entropy)
	representation.
	'''

	val = term.value

	d = "%d" % abs(val)
	x = "%x" % abs(val)
	sd = _entropy(d, "0123456789")
	sx = _entropy(x, "0123456789abcdef")
	if sx < sd:
		rep = hex(val)
	else:
		rep = str(val)

	return term.factory.makeStr(rep)

intlit = combine.Composition(intrepr, box.const)

@util.Adaptor
def strrepr(term):
	val = term.value
	if val[-1:] == '\0':
		val = val[:-1]
	res = '"'
	for c in val:
		if c in ('"', '\\'):
			res += '\\' + c
		elif ord(c) >= 32 and ord(c) < 128:
			res += c
		elif c == '\n':
			res += '\\n'
		elif c == '\t':
			res += '\\t'
		elif c == '\r':
			res += '\\r'
		else:
			res += '\\' + oct(ord(c))
	res += '"'
	return term.factory.makeStr(res)

strlit = combine.Composition(strrepr, box.const)


parse.Transfs('''

#######################################################################
# Types

ppSign =
	Signed -> H([ <kw "signed">, " " ])
|	Unsigned -> H([ <kw "unsigned"> , " " ])
|	NoSign -> ""

ppSize =
	switch id
	case 8:
		!<kw "char">
	case 16:
		!H([ <kw "short">, " ", <kw "int"> ])
	case 32:
		!<kw "int">
	case 64:
		!H([ <kw "long">, " ", <kw "int"> ])
	else
		!H([ "int", <strings.tostr> ])
	end

ppType =
	Void
		-> <kw "void">
|	Bool
		-> <kw "bool">
|	Int(size, sign)
		-> H([ <ppSign sign>, <ppSize size> ])
|	Float(32)
		-> <kw "float">
|	Float(64)
		-> <kw "double">
|	Char(8)
		-> <kw "char">
|	Char(16)
		-> <kw "wchar_t">
|	Pointer(type)
		-> H([ <ppType type>, " ", <ppOp "*"> ])
|	Array(type)
		-> H([ <ppType type>, "[", "]" ])
|	Blob(size)
		-> H([ "blob", <strings.tostr size> ])
|	_ -> "???"


#######################################################################
# Operator precendence.
#
# See http://www.difranco.net/cop2220/op-prec.htm

precUnaryOp =
	Not -> 1
|	Neg -> 1

precBinaryOp =
	And(Bool) -> 10
|	Or(Bool) -> 11
|	And(_) -> 7
|	Or(_) -> 9
|	Xor(_) -> 8
|	LShift -> 4
|	RShift -> 4
|	Plus -> 4 # force parenthesis inside shifts (was 3)
|	Minus -> 4 # force parenthesis inside shifts (was 3)
|	Mult -> 2
|	Div -> 2
|	Mod -> 2
|	Eq -> 6
|	NotEq -> 6
|	Lt -> 5
|	LtEq -> 5
|	Gt -> 5
|	GtEq -> 5

precExpr =
	Lit(_, _) -> 0
|	Sym(_) -> 0
|	Cast(_, _) -> 1
|	Addr(_) -> 1
|	Ref(_) -> 1
|	Unary(op, _) -> <precUnaryOp op>
|	Binary(op, _, _) -> <precBinaryOp op>
|	Cond(_, _, _) -> 13
|	Call(_, _) -> 0


#######################################################################
# Expressions

ppUnaryOp =
	Not(Bool) -> "!"
|	Not(_) -> "~"
|	Neg -> "-"

ppBinaryOp =
	And(Bool) -> "&&"
|	Or(Bool) -> "||"
|	And(_) -> "&"
|	Or(_) -> "|"
|	Xor(_) -> "^"
|	LShift -> "<<"
|	RShift -> ">>"
|	Plus -> "+"
|	Minus -> "-"
|	Mult -> "*"
|	Div -> "/"
|	Mod -> "%"
|	Eq -> "=="
|	NotEq -> "!="
|	Lt -> "<"
|	LtEq -> "<="
|	Gt -> ">"
|	GtEq -> ">="


SubExpr(Cmp) =
	?[pprec, rest] ;
	prec := precExpr rest ;
	if Cmp(!prec, !pprec) then
		!H([ "(", <exprKern [prec,rest]>, ")" ])
	else
		exprKern [prec,rest]
	end


subExpr = SubExpr(arith.Gt)
subExprEq = SubExpr(arith.Geq)

exprKern =
	( [prec,rest] -> rest ) ;
	Path((
	Lit(Int(_,_), value)
		-> <intlit value>
|	Lit(Pointer(Char(8)), value)
		-> <strlit value>
|	Lit(type, value)
		-> <lit value>
|	Sym(name)
		-> <sym name>
|	Cast(type, expr)
		-> H([ "(", <ppType type>, ")", " ", <subExpr [prec,expr]> ])
|	Unary(op, expr)
		-> H([ <ppUnaryOp op>, <subExpr [prec,expr]> ])
|	Binary(op, lexpr, rexpr)
		-> H([ <subExpr [prec,lexpr]>, " ", <ppBinaryOp op>, " ", <subExprEq [prec,rexpr]> ])
|	Cond(cond, texpr, fexpr)
		-> H([ <subExpr [prec,cond]>, " ", <ppOp "?">, " ", <subExpr [prec,texpr]>, " ", <ppOp ":">, " ", <subExpr [prec,fexpr]> ])
|	Call(addr, args)
		-> H([ <subExpr [prec,addr]>, "(", <(Map(subExpr [prec,<id>]); commas) args>, ")" ])
|	Addr(addr)
		-> H([ <ppOp "&">, <subExpr [prec,addr]> ])
|	Ref(expr)
		-> H([ <ppOp "*">, <subExpr [prec,expr]> ])
))

ppExpr =
	exprKern [<precExpr>,<id>]


#######################################################################
# Statements

ppArg =
	Arg(type, name)
		-> H([ <ppType type>, " ", name ])

ppStmts =
	!V( <Map(ppStmt)> )


stmtKern =
	Assign(Void, NoExpr, src)
		-> H([ <ppExpr src> ])
|	Assign(_, dst, src)
		-> H([ <ppExpr dst>, " ", <ppOp "=">, " ", <ppExpr src> ])
|	If(cond, _, _)
		-> H([ <kw "if">, "(", <ppExpr cond>, ")" ])
|	While(cond, _)
		-> H([ <kw "while">, "(", <ppExpr cond>, ")" ])
|	DoWhile(cond, _)
		-> H([ <kw "while">, "(", <ppExpr cond>, ")" ])
|	Var(type, name, NoExpr)
		-> H([ <ppType type>, " ", name ])
|	Var(type, name, val)
		-> H([ <ppType type>, " ", name, " = ", <ppExpr val> ])
|	Function(type, name, args, stmts)
		-> H([ <ppType type>, " ", name, "(", <(Map(ppArg);commas) args>, ")" ])
|	Label(name)
		-> H([ name, ":" ])
|	GoTo(label)
		-> H([ <kw "goto">, " ", <ppExpr label> ])
|	Ret(_, NoExpr)
		-> H([ <kw "return"> ])
|	Ret(_, value)
		-> H([ <kw "return">, " ", <ppExpr value> ])
|	NoStmt
		-> ""
|	Asm(opcode, operands)
		-> H([ <kw "asm">, "(", <commas [<lit opcode>, *<Map(ppExpr) operands>]>, ")" ])

ppLabel =
	Label
		-> D( <stmtKern> )

ppBlock =
	Block( stmts )
		-> V([
			D("{"),
				<ppStmts stmts>,
			D("}")
		])

ppIf =
	If(_, true, NoStmt)
		-> V([
			<stmtKern>,
				I( <ppStmt true> )
		])
|	If(_, true, false)
		-> V([
			<stmtKern>,
				I( <ppStmt true> ),
			H([ <kw "else"> ]),
				I( <ppStmt false> )
		])

ppWhile =
	While(_, body)
		-> V([
			<stmtKern>,
				I( <ppStmt body> )
		])

ppDoWhile =
	DoWhile(_, body)
		-> V([
			H([ <kw "do"> ]),
				I( <ppStmt body> ),
			!H([ <stmtKern>, ";" ])
		])

ppFunction =
	Function(_, _, _, stmts)
		-> D(V([
			<stmtKern>,
			"{",
				I(V([ <ppStmts stmts> ])),
			"}"
		]))

ppDefault =
	!H([ <stmtKern>, ";" ])

ppStmt = Path(
	switch project.name
		case "Label": ppLabel
		case "Block": ppBlock
		case "If": ppIf
		case "While": ppWhile
		case "DoWhile": ppDoWhile
		case "Function": ppFunction
		else ppDefault
	end
)

module = Path((
	Module(stmts)
		-> V([
			I( <ppStmts stmts> )
		])
))

''')


#######################################################################
# Test


if __name__ == '__main__':
	from aterm.factory import factory
	import sys

	def run(fp):
		term = factory.readFromTextFile(fp)
		boxes = module(term)
		sys.stdout.write(box.stringify(boxes))

	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			run(open(arg, "rb"))
	else:
		run(sys.stdin)



