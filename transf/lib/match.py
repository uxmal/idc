'''Term matching transformations.'''


import aterm.factory
import aterm.types
import aterm.term
import aterm.project

from transf import exception
from transf import transformation
from transf import variable
from transf.lib import base
from transf.lib import combine
from transf.lib import project
from transf.lib import _common
from transf import util


_factory = aterm.factory.factory


anInt = util.BoolAdaptor(aterm.types.isInt)
aStr = util.BoolAdaptor(aterm.types.isStr)
aReal = util.BoolAdaptor(aterm.types.isReal)
aList = util.BoolAdaptor(aterm.types.isList)
anAppl = util.BoolAdaptor(aterm.types.isAppl)


class _Term(_common._Term):

	def apply(self, term, ctx):
		if self.term == term:
			return term
		else:
			raise exception.Failure('term mismatch', self.term, term)

def Term(term):
	return _common.Term(term, _Term)


class TermSet(transformation.Transformation):

	def __init__(self, terms):
		transformation.Transformation.__init__(self)
		self.terms = {}
		for term in terms:
			if isinstance(term, basestring):
				term = _factory.parse(term)
			else:
				assert isinstance(term, aterm.term.Term)
			self.terms[term] = None

	def apply(self, term, ctx):
		if term in self.terms:
			return term
		else:
			raise exception.Failure('term not in set', term)


def Int(value):
	'''Transformation which matches an integer term with the given value.'''
	return _common.Int(value, _Term)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)


def Real(value):
	'''Transformation which matches a real term with the given value.'''
	return _common.Real(value, _Term)


def Str(value):
	'''Transformation which matches a string term with the given value.'''
	return _common.Str(value, _Term)

empty = Str("")


def StrSet(values):
	return TermSet([_factory.makeStr(value) for value in values])


class Nil(_Term):
	'''Transformation which matches an empty list term.'''

	# XXX: we subclass _Term in orde to save time in apply

	def __init__(self):
		_Term.__init__(self, _factory.makeNil())

	def apply(self, term, ctx):
		if not aterm.types.isNil(term):
			raise exception.Failure('term is not an empty list', term)
		return term

nil = Nil()


class _ConsL(_common._Cons):

	def apply(self, term, ctx):
		try:
			head = term.head
			tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list construction term', term)
		else:
			self.head.apply(head, ctx)
			self.tail.apply(tail, ctx)
			return term

def ConsL(head, tail):
	return _common.Cons(head, tail, _ConsL, _Term)


class _ConsR(_common._Cons):

	def apply(self, term, ctx):
		try:
			head = term.head
			tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list construction term', term)
		else:
			self.tail.apply(tail, ctx)
			self.head.apply(head, ctx)
			return term

def ConsR(head, tail):
	return _common.Cons(head, tail, _ConsR, _Term)


Cons = ConsL


def List(elms, tail = None):
	return _common.List(elms, tail, Cons, nil)


class Appl(_common.Appl):

	def apply(self, term, ctx):
		try:
			term_name = term.name
			term_args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)
		else:
			if self.name != term_name:
				raise exception.Failure('application name mismatch', self.name, term_name)
			if len(self.args) != len(term_args):
				raise exception.Failure
			for self_arg, term_arg in zip(self.args, term_args):
				self_arg.apply(term_arg, ctx)
			return term

def ApplName(name):
	return combine.Where(combine.Composition(project.name, Str(name)))

def ApplNames(names):
	return combine.Where(combine.Composition(project.name, StrSet(names)))

class ApplCons(_common.ApplCons):

	def apply(self, term, ctx):
		try:
			name = term.name
			args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)
		else:
			factory = term.factory
			self.name.apply(factory.makeStr(name), ctx)
			self.args.apply(factory.makeList(args), ctx)
			return term


def Var(var):
	assert isinstance(var, variable.Variable)
	return var.match


class Annos(_common.Annos):

	def apply(self, term, ctx):
		annos = aterm.project.annotations(term)
		self.annos.apply(annos, ctx)
		return term


def Anno(anno):
	from transf.lib import traverse
	return Annos(traverse.One(combine.Where(anno)))
