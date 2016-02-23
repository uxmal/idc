/*
 * Parser for AT&T syntax assembly.
 *
 * See also:
 * - http://l4hq.org/cvsweb/cvsweb/~checkout~/afterburner/asm-parser/Asm.g
 */

header {
import sys
}

header "att_parser.__main__" {
    from att_lexer import Lexer
    from aterm.factory import factory

    lexer = Lexer()
    parser = Parser(lexer, factory = factory)
    term = parser.start()

    print "** ANTLR AST **"
    ast = parser.getAST()
    print ast.toStringList()
    print

    print "** Aterm AST **"
    print str(term)
    print

    from transf.exception import Failure
    from ir import pprint
    from box import stringify
    try:
        text = stringify(pprint.module(term))
        print "** C pretty-print **"
        print text
        print
    except Failure:
        pass
}

header "att_parser.__init__" {
    self.factory = kwargs["factory"]
    self.counter = 0
}

options {
    language  = "Python";
}

class att_lexer extends Lexer;
options {
	k = 2;
}

DOTSYMBOL: '.' ('a'..'z'|'A'..'Z'|'_'|'.'|'$'|'0'..'9')*;

SYMBOL: ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'_'|'.'|'$'|'@'|'0'..'9')*;





BINARY: '0' ('b'|'B')! ('0'|'1')*;
HEXADECIMAL: '0' ('x'|'X') ('0'..'9'|'a'..'f'|'A'..'F')*;
OCTAL: '0' ('0'..'9')*;
DECIMAL: '1'..'9' ('0'..'9')*;

// TODO: float point numbers

PERCENTAGE: '%';
DOLLAR: '$';
COMMA: ',';
COLON: ':';
protected
SEMI: ';';
AT: '@';

LPAR: '(';
RPAR: ')';


MINUS: '-';
PLUS: '+';
STAR: '*';

CHAR
	:	'\'' (ESC|~'\'') '\''
	;

STRING
	:	'"'! (ESC|~'"')* '"'!
	;

protected
ESC	: '\\'!
		( 'n' { $setText("\n") }
		| 'r' { $setText("\r") }
		| 't' { $setText("\t") }
		| 'b' { $setText("\b") }
		| 'f' { $setText("\f") }
		| '"' { $setText("\"") }
		| '\'' { $setText("'") }
		| '\\' { $setText("\\") }
		|
			( '0'..'3'
				( options { warnWhenFollowAmbig = false; }
				:	'0'..'9'
					( options { warnWhenFollowAmbig = false; }
					:	'0'..'9'
					)?
				)?
			| '4'..'7'
				( options { warnWhenFollowAmbig = false; }
				:	'0'..'9'
				)?
			)
			{
                n = $getText
                $setText(chr(int(n, 8)))
            }
		)
	;


// Whitespace -- ignored
WS  :
        (   ' '
        |   '\t'
        |   '\f'
        )
        { $setType(SKIP); }
    ;

EOL
    :
        (   "\r\n"  // DOS
        |   '\r'    // Macintosh
        |   '\n'    // Unix
        )
        { $newline; }
    | SEMI
    ;

// Single-line comments
SL_COMMENT
	:	"#"
		(~('\n'|'\r'))* ('\n'|'\r'('\n')?)?
		{ $newline; $setType(SKIP); }
	;

// multiple-line comments
//ML_COMMENT
// 	:	"/*"
// 		(
// 			{ LA(2)!='/' }? '*'
// 		|	'\r' '\n'		{newline();}
// 		|	'\r'			{newline();}
// 		|	'\n'			{newline();}
// 		|	~('*'|'\n'|'\r')
// 		)*
// 		"*/"
// 		{$setType(Token.SKIP);}
// 	;

class att_parser extends Parser;
options {
	buildAST=true; // TODO: remove -- only used for debugging
	k = 3;
	defaultErrorHandler = false;
}

{
    def data_constant(self, type, prefix, value):
        self.counter += 1
        type = self.factory.make(type)
        name = prefix + str(self.counter)
        return self.factory.make("Var(type,name,Lit(type,value))", type=type, name=name, value=value)
}

start returns [res]
		{ insns = [] }
	:
		( s=statement
			{ insns.extend(s) }
		)* EOF
		{ res = self.factory.make("Module(insns)", insns = insns) }
	;

statement returns [res]
	: lbls=labels isns=tail EOL
		{ res = lbls + isns }
 	;

labels returns [res]
	: ( symbol COLON ) => (lbl=symbol COLON^ lbls=labels)
		{
            res = [self.factory.make("Label(lbl)", lbl=lbl)]
            res.extend(lbls)
        }
	| /* no label */
		{ res = [] }
	;

tail returns [res]
	: res=directive
	| res=prefixed_instruction
	| /* empty statement */
		{ res = [] }
	;

directive returns [res]
	: d:DOTSYMBOL^
		{ directive = #d.getText() }
		( { directive == ".byte" }? res=integer_constant[8]
		| { directive == ".word" }? res=integer_constant[16]
		| { directive == ".long" }? res=integer_constant[32]
		| { directive == ".int" }? res=integer_constant[32]
		| { directive == ".quad" }? res=integer_constant[64]
		| { directive == ".ascii" }? res=ascii_constant
		| ( ~EOL )*
			// FIXME: Do not ignore directives
			{ res = [] }
		)
	;

integer_constant[size] returns [res]
	: i=integer
		{ res = [self.data_constant("Int(%d,NoSign)" % size, "i_", i)] }
	;

ascii_constant returns [res]
	: s:STRING
		{ res = [self.data_constant("Pointer(Char(8))", "s_", #s.getText())] }
	;

prefixed_instruction returns [res]
	: ( instruction ) => insn=instruction
		{ res = [insn] }
	| SYMBOL insn=instruction
		// FIXME: Do not ignore instruction prefixes
		{ res = [insn] }
	;

instruction returns [res]
		{ operands = [] }
	: opcode:SYMBOL^ ( o=operand { operands.append(o) } ( COMMA! o=operand { operands.append(o) } )* )?
		{
            // reverse operands to intel syntax
            if len(operands) == 2:
                operands.reverse()
            res = self.factory.make("Asm(_, _)", #opcode.getText().lower(), operands)
		}
	;

operand returns [res]
	:
		( ( register ~COLON ) => o=register
			{ res = o }
		| o=immediate
			{ res = o }
		| o=memory
			{ res = o }
		| ( STAR register ~COLON ) => STAR o=register
			{ res = self.factory.make("Ref(_)", o) }
		| STAR o=memory
			{ res = o }
		)
	;

immediate returns [ret]
	: DOLLAR^ c=constant
		{ ret = c }
	;

register returns [ret]
	: PERCENTAGE^ name=symbol
		{ ret = self.factory.make("Sym(_){Reg}", name) }
	;

memory returns [ret]
		{
            disp = None
            base = None
		}
	:
		( section=register COLON! )?
            // XXX: section is ignored
		( disp=constant ( base=memory_base )? | base=memory_base )
		{
            if base is None:
                addr = disp
            elif disp is None:
                addr = base
            else:
                addr = self.factory.make("Binary(Plus(Int(32,Signed)),_,_)", base, disp)
            ret = self.factory.make("Ref(_)", addr)
		}
	;

memory_base returns [ret]
		{
            base = None
            index = None
            scale = 1
		}
	: LPAR! (base=register)? ( COMMA! (index=register)? ( COMMA! (scale=integer)? )? )? RPAR!
		{
            if not index is None and scale != 1:
                scale = self.factory.make("Lit(Int(32,Signed),_))", scale)
                index = self.factory.make("Binary(Plus(Int(32,Signed)),_,_)", index, scale)
            if base is None:
                ret = index
            elif index is None:
                ret = base
            else:
                ret = self.factory.make("Binary(Plus(Int(32,Signed)),_,_)", base, index)
		}
	;

constant returns [ret]
	: sym=symbol
		{ ret = self.factory.make("Sym(_)", sym) }
	| value=integer
		{ ret = self.factory.make("Lit(Int(32,Signed),_)", value) }
	;

symbol returns [name]
	:
		( d:DOTSYMBOL
			{ name = #d.getText() }
		| i:SYMBOL
			{ name = #i.getText() }
		)
	;

integer returns [value]
	:
		( b:BINARY
			{ value = int(#b.getText()[2:], 2) }
		| o:OCTAL
			{ value = int(#o.getText(), 8) }
		| d:DECIMAL
			{ value = int(#d.getText()) }
		| h:HEXADECIMAL
			{ value = int(#h.getText()[2:], 16) }
		| MINUS^ i=integer
			{ value = -i }
		)
	;
