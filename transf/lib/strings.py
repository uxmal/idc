'''String manipulation transformations.'''


import aterm.convert

from transf import exception
from transf import transformation
from transf import operate
from transf.lib import combine
from transf.lib import build
from transf.lib import unify


class ToStr(transformation.Transformation):

	def apply(self, term, ctx):
		try:
			return term.factory.makeStr(str(term.value))
		except AttributeError:
			raise exception.Failure('not a literal term', term)

tostr = ToStr()


class _Concat2(operate.Binary):

	def apply(self, term, ctx):
		head = self.loperand.apply(term, ctx)
		tail = self.roperand.apply(term, ctx)
		try:
			head_value = aterm.convert.toStr(head)
			tail_value = aterm.convert.toStr(tail)
		except TypeError:
			raise exception.Failure('not string terms', head, tail)
		return term.factory.makeStr(head_value + tail_value)

def Concat2(loperand, roperand):
	'''Concatenates two lists.'''
	if loperand is build.empty:
		return roperand
	if roperand is build.empty:
		return loperand
	return _Concat2(loperand, roperand)

concat = unify.Foldr(build.empty, Concat2)
