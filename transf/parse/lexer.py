"""Custom transformation lexer."""


import antlr
import antlrre

from transf.parse import parser


# python string reg. exp.
_pystr = \
	r"'''(?:\\.|.)*?'''|" \
	r'"""(?:\\.|.)*?"""|' \
	r'"(?:\\.|.)*?"|' \
	r"'(?:\\.|.)*?'"

# python comment reg. exp.
_pycomm = \
	r'#[^\r\n]*'

# python object reg. exp.
_pyobj = '`(?:' + _pycomm + '|' + _pystr + '|[^`]*)`'


_HEX = 1001


_tokenizer = antlrre.Tokenizer(
	# token regular expression table
	tokens = [
		# whitespace and comments
		(parser.SKIP,
			r'[ \t\f\r\n]+|'
			r'#[^\r\n]*',
		False),

		# REAL
		(parser.REAL, r'-?(?:'
			r'(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|'
			r'[0-9]+[eE][-+]?[0-9]+'
		r')', False),

		# HEX
		(_HEX, r'-?0[xX][0-9a-fA-F]+', False),

		# INT
		(parser.INT, r'-?[0-9]+', False),

		# STR
		(parser.STR, r'"[^"\\]*(?:\\.[^"\\]*)*"', False),

		# IDs
		(parser.ID,
			r'_[a-zA-Z0-9_]+|'
			r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+',
		False),
		(parser.UID, r'[A-Z][a-zA-Z0-9_]*', False),
		(parser.LID, r'[a-z][a-zA-Z0-9_]*', True),

		(parser.ASSIGN, r':=', False),
		(parser.RARROW, r'->', False),
		(parser.RDARROW, r'=>', False),

		(parser.OBJ, _pyobj, False),
	],

	# symbol table
	symbols = {
		'_': parser.WILDCARD,
		'(': parser.LPAREN,
		')': parser.RPAREN,
		'[': parser.LSQUARE,
		']': parser.RSQUARE,
		'{': parser.LCURLY,
		'}': parser.RCURLY,
		'<': parser.LANGLE,
		'>': parser.RANGLE,
		',': parser.COMMA,
		':': parser.COLON,
		';': parser.SEMI,
		'*': parser.STAR,

		'\\': parser.RSLASH,
		'/': parser.LSLASH,

		'?': parser.QUEST,
		'!': parser.BANG,
		'+': parser.PLUS,
		'&': parser.AMP,
		'|': parser.VERT,
		'~': parser.TILDE,
		'=': parser.EQUAL,
	},

	# literal table
	literals = {
		"id": parser.IDENT,
		"fail": parser.FAIL,
		"if": parser.IF,
		"then": parser.THEN,
		"elif": parser.ELIF,
		"else": parser.ELSE,
		"end": parser.END,
		"in": parser.IN,
		"with": parser.WITH,
		"rec": parser.REC,
		"switch": parser.SWITCH,
		"case": parser.CASE,
		"shared": parser.SHARED,
		"where": parser.WHERE,
		"as": parser.AS,
	}
)


class Lexer(antlrre.TokenStream):

	tokenizer = _tokenizer

	def filterToken(self, type, text):
		if type == parser.STR:
			text = text[1:-1]
			text = text.replace('\\r', '\r')
			text = text.replace('\\n', '\n')
			text = text.replace('\\t', '\t')
			text = text.replace('\\', '')
		elif type == parser.OBJ:
			text = text[1:-1]
		elif type == _HEX:
			type = parser.INT
			text = str(int(text, 16))
		return type, text
