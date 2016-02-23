/*
 * Generate an aterm from an ANTLR AST.
 *
 * TODO: Implement thi as a baseclass instead of a TreeParse
 */

header {
import antlr
import aterm.factory
}

options {
	language = "Python";
}

class antlraterm extends TreeParser;

options {
	defaultErrorHandler = false;
}

aterm returns [ret]
	: #( ATINT i:. )
		{ ret = aterm.factory.factory.makeInt(int(#i.getText())) }
	| #( ATREAL r:. )
		{ ret = aterm.factory.factory.makeReal(float(#r.getText())) }
	| #( ATSTR s:. )
		{ ret = aterm.factory.factory.makeStr(#s.getText()) }
	| #( ATLIST l=aterm_list )
		{ ret = l }
	| #( n:ATAPPL args=aterm_args )
		{ name = #n.getText() }
		{ ret = aterm.factory.factory.makeAppl(name, args) }
	;

aterm_list returns [ret]
	: h=aterm t=aterm_list
		{ ret = aterm.factory.factory.makeCons(h, t) }
	|
		{ ret = aterm.factory.factory.makeNil() }
	;

aterm_args returns [ret]
:
		{ ret = [] }
	( a=aterm
		{ ret.append(a) }
	)*
;
