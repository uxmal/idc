/*
 * Grammar for generating term transformations.
 *
 * The syntax is inspired on:
 * - the Stratego language;
 * - Haskell language.
 */


header {
    __doc__ = "Transformation language parsing."

    __all__ = [
        "SemanticException",
        "Parser",
    ]

    import antlr
    import aterm.factory
    import transf

    class SemanticException(antlr.SemanticException):

        def __init__(self, node, msg):
            antlr.SemanticException.__init__(self)
            self.node = node
            self.msg = msg

        def __str__(self):
            line = self.node.getLine()
            col  = self.node.getColumn()
            text = self.node.getText()
            return "line %s:%s: \"%s\": %s" % (line, col, text, self.msg)

        __repr__ = __str__
}


options {
	language = "Python";
}


class parser extends Parser;

options {
	k=2;
	buildAST = true;
	defaultErrorHandler = false;
	importVocab = antlraterm;
}

tokens {
	// TODO: describe more tokens
	IN="in";
}

{
    __doc__ = "Parser for transformation language."
}

definitions
	: ( definition )* EOF!
		{ ## = #(#[ATAPPL,"Defs"],#(#[ATLIST], ##)) }
	;

definition
	: SHARED! id type
		{ ## = #(#[ATAPPL,"VarDef"], ##) }
	| id EQUAL! transf
		{ ## = #(#[ATAPPL,"TransfDef"], ##) }
	| id LPAREN! id_list RPAREN! EQUAL! transf
		{ ## = #(#[ATAPPL,"MacroDef"], ##) }
	;

type
	:
		{ ## = #(#[ATSTR],#[ID,"term"]) }
	| LSQUARE! RSQUARE!
		{ ## = #(#[ATSTR],#[ID,"table"]) }
	| AS! id
	;

common_atom
	: QUEST! term
		{ ## = #(#[ATAPPL,"Match"], ##) }
	| BANG! term
		{ ## = #(#[ATAPPL,"Build"], ##) }
	| TILDE! term
		{ ## = #(#[ATAPPL,"Congruent"], ##) }
	;

transf
	: transf_where
	;

transf_atom
	: common_atom
	| IDENT!
		{ ## = #(#[ATAPPL,"Ident"], ##) }
	| FAIL!
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	// TODO: Add an assert statement
	| LPAREN! transf RPAREN!
	| IF! if_clauses if_else END!
		{ ## = #(#[ATAPPL,"If"], ##) }
	| SWITCH! transf switch_cases switch_else END!
		{ ## = #(#[ATAPPL,"Switch"], ##) }
	| WITH! id_list IN! transf END!
		{ ## = #(#[ATAPPL,"Scope"], ##) }
	| LCURLY! id_list COLON! transf RCURLY!
		{ ## = #(#[ATAPPL,"Scope"], ##) }
	| REC! id COLON! transf_atom
		{ ## = #(#[ATAPPL,"Rec"], ##) }
	| id
		{ ## = #(#[ATAPPL,"Transf"], ##) }
	| id LPAREN! args RPAREN!
		{ ## = #(#[ATAPPL,"Macro"], ##) }
	;

args
	: ( arg ( COMMA! arg )* )?
		{ ## = #(#[ATLIST], ##) }
	;

arg
	: transf_choice
	| ( /* INT | REAL | STR | */ OBJ )
		{ ## = #(#[ATAPPL,"Obj"], #(#[ATSTR],##)) }
	;

if_clauses
	: if_clause (ELIF! if_clause)*
		{ ## = #(#[ATLIST], ##) }
	;

if_clause
	: transf THEN! transf
		{ ## = #(#[ATAPPL,"IfClause"], ##) }
	;

if_else
	: ELSE! transf
	|
		{ ## = #(#[ATAPPL,"Ident"], ##) }
	;

switch_cases
	: ( switch_case )*
		{ ## = #(#[ATLIST], ##) }
	;

switch_case
	: CASE! switch_case_terms COLON! transf
		{ ## = #(#[ATAPPL,"SwitchCase"], ##) }
	;

switch_case_terms
	: term ( COMMA! term )*
		{ ## = #(#[ATLIST], ##) }
	;

switch_else
	: ELSE! (COLON!)? transf
	|
		{ ## = #(#[ATAPPL,"Fail"], ##) }
	;

var_defs
	: var_def ( COMMA! var_def )*
		{ ## = #(#[ATLIST], ##) }
	;

var_def
	: id EQUAL! transf
		{ ## = #(#[ATAPPL,"WithDef"], ##) }
	;

transf_build_apply
	: ( term_atom ( RARROW! | ASSIGN! ) ) => term_atom
		( RARROW! term_atom
			( IF! transf_atom
				{ ## = #(#[ATAPPL,"RuleIf"], ##) }
			|
				{ ## = #(#[ATAPPL,"Rule"], ##) }
			)
		| ASSIGN! transf_build_apply
			{ ## = #(#[ATAPPL,"ApplyAssign"], ##) }
		)
	| transf_atom
		( options { warnWhenFollowAmbig=false; }
 			// ambiguous case: definition follows
 		: ( id ( LPAREN! id_list RPAREN! )? EQUAL! ) =>
		| term
			{ ## = #(#[ATAPPL,"BuildApply"], ##) }
		)?
	;

transf_apply_match
	: transf_build_apply
		( RDARROW! term
			{ ## = #(#[ATAPPL,"ApplyMatch"], ##) }
		)*
	;

transf_merge
	:! l:transf_apply_match
		( n:merge_names r:transf_apply_match
			{ ## = #(#[ATAPPL,"Join"], #l, #r, #n) }
		|
			{ ## = #l }
		)
	|! n2:merge_names STAR! o:transf_apply_match
		{ ## = #(#[ATAPPL,"Iterate"], #o, #n2) }
	;

merge_names
	: merge_union_names merge_opt_isect_names
	|! i:merge_isect_names u:merge_opt_union_names
		{ ## = #i }
		{ ##.setNextSibling(#u) }
	;

merge_union_names
	: LSLASH! id_list RSLASH!
	;

merge_isect_names
	: RSLASH! id_list LSLASH!
	;

merge_opt_union_names
	: merge_union_names
	|
		{ ## = #(#[ATLIST]) }
	;

merge_opt_isect_names
	: merge_isect_names
	|
		{ ## = #(#[ATLIST]) }
	;

transf_composition
	: transf_merge
		( SEMI! transf_composition
			{ ## = #(#[ATAPPL,"Composition"], ##) }
		)?
	;

transf_choice
	: transf_composition
		( AMP! transf_composition PLUS! transf_choice
			{ ## = #(#[ATAPPL,"GuardedChoice"], ##) }
		| PLUS! transf_choice
			{ ## = #(#[ATAPPL,"LeftChoice"], ##) }
		)?
	;

transf_rule
	: transf_choice
	;

transf_undeterministic_choice
	: transf_rule
		( ( VERT! transf_rule )+
			{ ## = #(#[ATAPPL,"Choice"], #(#[ATLIST],##)) }
		)?
	;

transf_where
	: transf_undeterministic_choice
		( WHERE! transf_rule
			{ ## = #(#[ATAPPL,"Where"], ##) }
		)?
	;

term
	: common_atom
	| term_atom
	;

term_atom
	: INT
		{ ## = #(#[ATAPPL,"Int"], #(#[ATINT],##)) }
	| REAL
		{ ## = #(#[ATAPPL,"Real"], #(#[ATREAL],##)) }
	| STR
		{ ## = #(#[ATAPPL,"Str"], #(#[ATSTR],##)) }
	| LSQUARE! term_list RSQUARE!
	| term_appl
		( LCURLY! term_list RCURLY!
			{ ## = #(#[ATAPPL,"Annos"], ##) }
		)?
	;

term_appl
	: term_name
		{ ## = #(#[ATAPPL,"ApplName"], ##) }
//	| term_args
//		{ ## = #(#[ATAPPL,"Appl"], #[ATSTR,""], ##) }
	| term_name term_args
		{ ## = #(#[ATAPPL,"Appl"], ##) }
	| ( term_var | term_wildcard | term_wrap )
		( LPAREN! term_list RPAREN!
			{ ## = #(#[ATAPPL,"ApplCons"], ##) }
		)?
	;

term_name
	: UID
		{ ## = #(#[ATSTR],##) }
	;

term_var
	: LID
		{ ## = #(#[ATAPPL,"Var"], #(#[ATSTR],##)) }
	;

term_args
	: LPAREN! ( term ( COMMA! term )* )? RPAREN!
		{ ## = #(#[ATLIST],##) }
	;

term_wildcard
	: WILDCARD!
		{ ## = #(#[ATAPPL,"Wildcard"]) }
	;

term_list
	: term_implicit_nil
	| term ( COMMA! term_list | term_implicit_nil )
		{ ## = #(#[ATAPPL,"Cons"], ##) }
	| STAR! ( term | term_implicit_wildcard )
		( COMMA! term_list
		{ ## = #(#[ATAPPL,"Cat"], ##) }
		)?
	;

term_implicit_nil
	:
		{ ## = #(#[ATAPPL,"Nil"]) }
	;

term_implicit_wildcard
	:
		{ ## = #(#[ATAPPL,"Wildcard"]) }
	;

term_wrap
	: LANGLE! transf RANGLE!
		{ ## = #(#[ATAPPL,"Wrap"], ##) }
	;

id_list
	: ( id ( COMMA! id )* )?
		{ ## = #(#[ATLIST],##) }
	;

id
	: ( ID | LID | UID )
		{ ## = #(#[ATSTR], ##) }
	;

