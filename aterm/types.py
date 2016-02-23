'''Term types constants.'''


INT  = 0x01
REAL = 0x02
STR  = 0x04
NIL  = 0x08
CONS = 0x10
APPL = 0x20

LIT  = INT | REAL | STR

LIST = NIL | CONS


def isInt(term):
	'''Integer term type verifier.'''
	return term.type == INT


def isReal(term):
	'''Real term type verifier.'''
	return term.type == REAL


def isStr(term):
	'''String term type verifier.'''
	return term.type == STR


def isLit(term):
	'''Literal term type verifier.'''
	return term.type & LIT


def isNil(term):
	'''Empty list term type verifier.'''
	return term.type == NIL


def isCons(term):
	'''List construction term type verifier.'''
	return term.type == CONS


def isList(term):
	'''List term type verifier.'''
	return term.type & LIST


def isAppl(term):
	'''Application term type verifier.'''
	return term.type == APPL
