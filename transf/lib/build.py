'''Term building transformations.

The transformations in this module build new terms from scratch, without taking
in consideration the input term.
'''


import aterm.factory
import aterm.term
import aterm.types

from transf import exception
from transf import transformation
from transf import variable
from transf.lib import base
from transf.lib import _common


_factory = aterm.factory.factory


class _Term(_common._Term):

	# NOTE: especial care should when deriving this class
	# to avoid breaking optimizations

	def __init__(self, term):
		transformation.Transformation.__init__(self)
		self.term = term

	def apply(self, term, ctx):
		return self.term

def Term(term):
	return _common.Term(term, _Term)


def Int(value):
	return _common.Int(value, _Term)

zero = Int(0)
one = Int(1)
two = Int(2)
three = Int(3)
four = Int(4)


def Real(value):
	return _common.Real(value, _Term)


def Str(value):
	return _common.Str(value, _Term)

empty = Str("")


_nil = _factory.makeNil()

def Nil():
	return _Term(_nil)

nil = Nil()


class _ConsL(_common._Cons):

	def apply(self, term, ctx):
		head = self.head.apply(term, ctx)
		tail = self.tail.apply(term, ctx)
		return term.factory.makeCons(head, tail)

def ConsL(head, tail):
	return _common.Cons(head, tail, _ConsL, _Term)


class _ConsR(_common._Cons):

	def apply(self, term, ctx):
		tail = self.tail.apply(term, ctx)
		head = self.head.apply(term, ctx)
		return term.factory.makeCons(head, tail)

def ConsR(head, tail):
	return _common.Cons(head, tail, _ConsR, _Term)


Cons = ConsL


def List(elms, tail = None):
	return _common.List(elms, tail, Cons, nil)


class Appl(_common.Appl):

	def apply(self, term, ctx):
		name = self.name
		args = [arg.apply(term, ctx) for arg in self.args]
		return term.factory.makeAppl(name, args)

class ApplCons(_common.ApplCons):

	def apply(self, term, ctx):
		name = self.name.apply(term, ctx)
		args = self.args.apply(term, ctx)
		# TODO: better type checking
		name = name.value
		args = tuple(args)
		return term.factory.makeAppl(name, args)


def Var(var):
	assert isinstance(var, variable.Variable)
	return var.build


class Annos(_common.Annos):

	def apply(self, term, ctx):
		if aterm.types.isAppl(term):
			annos = self.annos.apply(term, ctx)
			return term.factory.makeAppl(term.name, term.args, annos)
		return term
