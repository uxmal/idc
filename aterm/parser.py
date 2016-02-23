"""Term parsing.

Based on the ATerm syntax.
"""


import antlr


__all__ = ["Parser"]


EOF                 = antlr.EOF
SKIP                 = antlr.SKIP
INT = 4
REAL = 5
STR = 6
LSQUARE = 7
RSQUARE = 8
CONS = 9
LPAREN = 10
RPAREN = 11
LCURLY = 12
RCURLY = 13
WILDCARD = 14
VAR = 15
COMMA = 16
STAR = 17


class Parser:
	"""Term parser."""

	def __init__(self, lexer):
		self.lexer = lexer
		self.tokenNames = _tokenNames
		self.consume()

	def getFilename(self) :
		return self.lexer.filename

	def consume(self):
		self.type, self.text = self.lexer.nextToken()
		self.lt = self.text
		self.la = self.type

	def match(self, t):
		if self.la != t:
			filename, line, col = self.lexer.getpos()
			lt = antlr.CommonToken(
				type = self.type,
				text = self.text,
				line = line,
				col = col
			)
			raise antlr.MismatchedTokenException(
			   self.tokenNames, lt, t, False, filename)
		else:
			self.consume()

	def term(self):
		la1 = self.la
		if la1 == INT:
			ival = self.lt
			self.consume()
			return self.handleInt(int(ival))
		elif la1 == REAL:
			rval = self.lt
			self.consume()
			return self.handleReal(float(rval))
		elif la1 == STR:
			sval = self.lt
			self.consume()
			return self.handleStr(sval)
		elif la1 == LSQUARE:
			self.consume()
			elms = self.term_list()
			self.match(RSQUARE)
			return elms
		elif la1 in [CONS,LPAREN]:
			if la1 == CONS:
				cname = self.lt
				self.consume()
				la1 = self.la
				if la1 == LPAREN:
					self.consume()
					args=self.term_args()
					self.match(RPAREN)
				else:
					args = []
				name = cname
			elif la1 == LPAREN:
				self.consume()
				args=self.term_args()
				self.match(RPAREN)
				name = ""
			else:
				assert False

			la1 = self.la
			if la1 == LCURLY:
				self.consume()
				annos=self.term_list()
				self.match(RCURLY)
				return self.handleAppl(name, args, annos)
			else:
				return self.handleAppl(name, args)

		elif la1 in [WILDCARD,VAR]:
			if la1 == WILDCARD:
				self.consume()
				res = self.handleWildcard()
			elif la1 == VAR:
				vname = self.lt
				self.consume()
				res = self.handleVar(vname)
			else:
				assert False

			la1 = self.la
			if la1 == LPAREN:
				self.consume()
				args=self.term_list()
				self.match(RPAREN)
				la1 = self.la
				if la1 == LCURLY:
					self.consume()
					annos=self.term_list()
					self.match(RCURLY)
					res = self.handleApplCons(res, args, annos)
				else:
					res = self.handleApplCons(res, args)
			return res

		else:
			raise antlr.NoViableAltException(self.lt, self.getFilename())

	def term_list(self):
		if self.la in [RSQUARE,RPAREN,RCURLY,STAR]:
			return self.term_list_tail()
		else:
			heads = [self.term()]
			comma = False
			while self.la==COMMA:
				self.consume()
				if self.la not in [INT,REAL,STR,LSQUARE,CONS,LPAREN,WILDCARD,VAR]:
					comma = True
					break
				heads.append(self.term())

			la1 = self.la
			if comma:
				tail = self.term_list_tail()
			elif la1 == COMMA:
				self.match(COMMA)
				tail=self.term_list_tail()
			else:
				tail = self.handleNil()

			for head in reversed(heads):
				tail = self.handleCons(head, tail)

		return tail

	def term_args(self):
		if self.la == RPAREN:
			return []
		else:
			res = [self.term()]
			while self.la == COMMA:
				self.consume()
				res.append(self.term())
			return res

	def term_list_tail(self):
		if  self.la == STAR:
			self.consume()
			if  self.la == VAR:
				vname = self.lt
				self.consume()
				return self.handleVar(vname)
			else:
				return self.handleWildcard()
		else:
			return self.handleNil()

	def handleInt(self, value):
		raise NotImplementedError

	def handleReal(self, value):
		raise NotImplementedError

	def handleStr(self, value):
		raise NotImplementedError

	def handleNil(self):
		raise NotImplementedError

	def handleCons(self, head, tail):
		raise NotImplementedError

	def handleAppl(self, name, args, annos=None):
		raise NotImplementedError

	def handleWildcard(self):
		raise NotImplementedError

	def handleVar(self, name):
		raise NotImplementedError

	def handleApplCons(self, name, args, annos=None):
		raise NotImplementedError


_tokenNames = [
	"<0>",
	"EOF",
	"<2>",
	"NULL_TREE_LOOKAHEAD",
	"INT",
	"REAL",
	"STR",
	"LSQUARE",
	"RSQUARE",
	"CONS",
	"LPAREN",
	"RPAREN",
	"LCURLY",
	"RCURLY",
	"WILDCARD",
	"VAR",
	"COMMA",
	"STAR"
]


