"""Abstract Syntax Definition.

Based on the ASDL:
 - http://www.cs.princeton.edu/~danwang/Papers/dsl97/dsl97.html
"""


import aterm.types

from sets import Set as set


###############################################################################
# Exception hierarchy


class MismatchException(Exception):
	'''Description exception.'''

	def __init__(self, msg, trm, expected=None, pname=None, cname=None, fname=None):
		Exception.__init__(self)
		self.msg = msg
		self.args = [trm,expected]
		self.pname = pname
		self.cname = cname
		self.fname = fname

	def __str__(self):
		s = ''
		if self.pname is not None:
			s += self.pname + ':'
		if self.cname is not None:
			s += self.cname + ':'
		if self.fname is not None:
			s += self.fname + ':'
		s += ' ' + self.msg + ': ' + " ".join(map(repr, self.args))
		return s


###############################################################################
# Class hierarchy


class Type:
	'''Abstract base class for field type description classes.'''

	def validate(self, spec, term, pname=None, cname=None, fname=None):
		raise NotImplementedError

	def __str__(self):
		raise NotImplementedError


class BuiltinType(Type):
	'''Built-in type description.'''

	def __init__(self, name, type):
		self.name = name
		self.type = type

	def validate(self, spec, term, pname=None, cname=None, fname=None):
		if not term.type & self.type:
			raise MismatchException(
				"builtin type mismatch",
				self.type, term.type,
				pname=pname, cname=cname, fname=fname
			)

	def __str__(self):
		return self.name


class UserType(Type):
	'''User-defined type description.'''

	def __init__(self, name):
		self.name = name

	def validate(self, spec, term, pname=None, cname=None, fname=None):
		spec.validate(self.name, term)

	def __str__(self):
		return self.name


class ListType(Type):
	'''List type description.'''

	def __init__(self, subtype):
		self.subtype = subtype

	def validate(self, spec, term, pname=None, cname=None, fname=None):
		if not aterm.types.isList(term):
			raise MismatchException(
				"list term expected",
				term,
				pname=pname, cname=cname, fname=fname
			)
		for subterm in term:
			self.subtype.validate(spec, subterm, pname=pname, cname=cname, fname=fname)

	def __str__(self):
		return "%s*" % (str(self.subtype),)


class OptionalType(Type):
	'''Optional type description.'''

	def __init__(self, subtype, optname):
		self.subtype = subtype
		self.optname = optname

	def validate(self, spec, term, pname=None, cname=None, fname=None):
		if aterm.types.isAppl(term) and term.name == self.optname and len(term.args) == 0:
			return
		else:
			self.subtype.validate(spec, term, pname=pname, cname=cname, fname=fname)

	def __str__(self):
		return "%s?" % (str(self.subtype),)


class Field:
	'''Constructor field description.'''

	def __init__(self, type, name=None):
		self.type = type
		self.name = name

	def validate(self, spec, term, pname=None, cname=None):
		self.type.validate(spec, term, pname=pname, cname=cname, fname=self.name)

	def __str__(self):
		if self.name:
			return "%s %s" % (str(self.type), self.name)
		else:
			return str(self.type)


class Constructor:
	'''Constructor description.'''

	def __init__(self, name, fields):
		self.name = name
		self.fields = fields

	def validate(self, spec, term, pname=None):
		if not aterm.types.isAppl(term):
			raise MismatchException(
				"not an application term",
				term,
				pname=pname, cname=self.name
			)
		if term.name != self.name:
			raise MismatchException(
				"application name mismatch",
				term,
				pname=pname, cname=self.name
			)
		if len(term.args) != len(self.fields):
			raise MismatchException(
				"wrong number of arguments",
				term,
				pname=pname, cname=self.name
			)
		for field, arg in zip(self.fields, term.args):
			field.validate(spec, arg, pname=pname, cname=self.name)

	def __str__(self):
		if self.fields:
			return '%s(%s)' % (self.name, ', '.join([str(field) for field in self.fields]))
		else:
			return self.name


class Production:
	'''Production description.'''

	def __init__(self, name, constructors):
		self.name = name
		self.constructors = {}
		for constructor in constructors:
			self.constructors[constructor.name] = constructor

	def validate(self, spec, term):
		if not aterm.types.isAppl(term):
			raise MismatchException(
				"not an application term",
				term,
				pname=self.name
			)
		try:
			cons = self.constructors[term.name]
		except KeyError:
			raise MismatchException(
				"unexpected term",
				term,
				pname=self.name
			)
		cons.validate(spec, term, pname=self.name)

	def subproductions(self, spec, skip):
		s = set()
		for constructor in self.constructors.itervalues():
			s.append(constructor.name)

	def __str__(self):
		cons = '\n\t| '.join([str(constructor) for constructor in self.constructors.itervalues()])
		return '%s\n\t= %s\n' % (self.name, cons)


class Description:
	'''AST description.'''

	def __init__(self, productions):
		self.productions = {}
		for production in productions:
			self.productions[production.name] = production

	def validate(self, productionName, term):
		try:
			production = self.productions[productionName]
		except KeyError:
			raise ValueError("undefined production %r" % productionName)
		production.validate(self, term)

	def __str__(self):
		return '\n'.join([str(production) for production in self.productions.itervalues()])



###############################################################################
# Parsing


def _buildParser():
	from pyparsing import Word, Group, Optional, Literal, delimitedList, OneOrMore, restOfLine, Suppress

	upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	lower = 'abcdefghijklmnopqrstuvwxyz'
	alpha = '_' + upper + lower
	alpha_num = alpha + '0123456789'

	consId = Word(upper, alpha_num)
	typeId = Word(lower + alpha_num)
	id = Word(upper + lower, alpha_num)

	field = Group(typeId + Optional(Literal("?") | Literal("*"), default="") + Optional(id, default=""))
	cons = Group(consId + Group(Optional(Suppress("(") + delimitedList(field, delim=",") + Suppress(")"))))
	prod = Group(typeId + Suppress("=") + Group(delimitedList(cons, delim="|")))
	spec = OneOrMore(prod)

	comment = '--' + restOfLine
	spec.ignore(comment)
	return spec

_parser = _buildParser()


def optionalize(name):
	'''Create an optional and unique construcion name from a
	type name.
	'''
	return 'No' + name.capitalize()


def parse(buf):
	"""Parse a ASDL description."""
	productions = _parser.parseString(buf)
	resProductions = []
	for productionName, constructors in productions:
		resConstructors = []
		for constructorName, fields in constructors:
			resFields = []
			for fieldType, fieldModifier, fieldName in fields:
				if fieldType == 'int':
					resType = BuiltinType(fieldType, aterm.types.INT)
				elif fieldType == 'real':
					resType = BuiltinType(fieldType, aterm.types.REAL)
				elif fieldType == 'string':
					resType = BuiltinType(fieldType, aterm.types.STR)
				elif fieldType == 'object':
					resType = BuiltinType(fieldType, aterm.types.LIT)
				else:
					resType = UserType(fieldType)
				if fieldModifier == '?':
					resType = OptionalType(resType, optionalize(fieldType))
				if fieldModifier == '*':
					resType = ListType(resType)
				resFields.append(Field(resType, fieldName))
			resConstructors.append(Constructor(constructorName, resFields))
		resProductions.append(Production(productionName, resConstructors))
	resDescription = Description(resProductions)
	return resDescription


###############################################################################
# Unit tests


import unittest


class TestAsd(unittest.TestCase):

	sampleDescription = '''
		stm = Compound(stm head, stm next)
			| Assign(identifier? lval, exp rval)
			| Print(exp* args)
		exp = Id(string)
			| Num(int)
			| Op(exp, binop, exp)
		binop = Plus | Minus | Times | Div
	'''

	def testParse(self):
		parse(self.sampleDescription)

	validateTestCases = [
		('exp', 'Id("a")', True),
		('exp', 'Num(1)', True),
		('exp', 'Op(Num(1),Plus,Num(1))', True),
		('stm', 'Print([])', True),
		('stm', 'Print([Num(1),Num(2)])', True),

		('exp', 'Id(1)', False),
		('exp', 'Num("a")', False),
		('exp', 'Op(Plus,Num(1),Num(1))', False),
		('stm', 'Print()', False),
	]

	def testValidate(self):
		asd = parse(self.sampleDescription)
		from aterm.factory import factory
		for productionName, termStr, expectedResult in self.validateTestCases:
			term = factory.parse(termStr)
			try:
				asd.validate(productionName, term)
			except MismatchException:
				result = False
				if expectedResult != False:
					raise
			else:
				result = True
			self.failUnlessEqual(result, expectedResult, "%s ~ %s" % (productionName, termStr))


if __name__ == "__main__":
	unittest.main()


