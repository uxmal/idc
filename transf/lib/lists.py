'''List manipulation transformations.

See also U{http://nix.cs.uu.nl/dist/stratego/strategoxt-manual-unstable-latest/manual/chunk-chapter/library-lists.html}.
'''


import aterm.lists

from transf import exception
from transf import transformation
from transf import types
from transf import operate
from transf.lib import base
from transf import util
from transf.lib import combine
from transf.lib import project
from transf.lib import match
from transf.lib import build
from transf.lib import congruent
from transf.lib import scope
from transf.lib import unify


class Length(transformation.Transformation):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		return len(trm)

length = Length()


class Reverse(transformation.Transformation):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		return aterm.lists.reverse(trm)

reverse = Reverse()


class Map(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		return aterm.lists.map(lambda trm: self.operand.apply(trm, ctx), trm)


class MapR(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		return aterm.lists.rmap(lambda trm: self.operand.apply(trm, ctx), trm)


class ForEach(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		for elm in trm:
			self.operand.apply(elm, ctx)
		return trm


class Filter(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		res = []
		for elm in trm:
			try:
				elm = self.operand.apply(elm, ctx)
			except exception.Failure:
				pass
			else:
				res.append(elm)
		return trm.factory.makeList(res)


class FilterR(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		accum = trm.factory.makeNil()
		for elm in reverse(trm):
			try:
				elm = self.operand.apply(elm, ctx)
			except exception.Failure:
				pass
			else:
				accum = trm.factory.makeCons(elm, accum)
		return accum


class Fetch(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		for elm in trm:
			try:
				return self.operand.apply(elm, ctx)
			except exception.Failure:
				pass
		raise exception.Failure


class One(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		head = []
		tail = trm
		while tail:
			elm = tail.head
			tail = tail.tail
			try:
				elm = self.operand.apply(elm, ctx)
			except exception.Failure:
				pass
			else:
				tail = trm.factory.makeCons(elm, tail)
				for elm in reversed(head):
					tail = trm.factory.makeCons(elm, tail)
				return tail
		raise exception.Failure


class _Concat2(operate.Binary):

	def apply(self, trm, ctx):
		head = self.loperand.apply(trm, ctx)
		tail = self.roperand.apply(trm, ctx)
		return aterm.lists.extend(head, tail)


def Concat2(loperand, roperand):
	'''Concatenates two lists.'''
	if loperand is build.nil:
		return roperand
	if roperand is build.nil:
		return loperand
	return _Concat2(loperand, roperand)


def Concat(*operands):
	'''Concatenates several lists.'''
	return operate.Nary(operands, Concat2, build.nil)

concat = unify.Foldr(build.nil, Concat2)


# FIXME: write non-recursive versions


class MapConcat(operate.Unary):

	def apply(self, trm, ctx):
		assert aterm.types.isList(trm)
		lsts = []
		for elm in trm:
			lst = self.operand.apply(elm, ctx)
			assert aterm.types.isList(lst)
			lsts.append(lst)
		res = trm.factory.makeNil()
		for lst in reversed(lsts):
			res = aterm.lists.extend(lst, res)
		return res


def AtSuffix(operand):
	atsuffix = util.Proxy()
	atsuffix.subject = combine.Choice(operand, congruent.Cons(base.ident, atsuffix))
	return atsuffix


def AtSuffixR(operand):
	atsuffix = util.Proxy()
	atsuffix.subject = combine.Choice(congruent.Cons(base.ident, atsuffix), operand)
	return atsuffix


# TODO: is there any way to avoid so much code duplication in the Split* transfs?

def Split(operand):
	tail = types.term.Term('tail')
	return scope.Scope((tail,),
		build.List((
			AtSuffix(
				match.Cons(operand, match.Var(tail)) *
				build.nil
			),
			build.Var(tail)
		))
	)


def SplitBefore(operand):
	tail = types.term.Term('tail')
	return scope.Scope((tail,),
		build.List((
			AtSuffix(
				congruent.Cons(operand, base.ident) *
				match.Var(tail) * build.nil
			),
			build.Var(tail)
		))
	)


def SplitAfter(operand):
	tail = types.term.Term('tail')
	return scope.Scope((tail,),
		build.List((
			AtSuffix(
				congruent.Cons(operand, match.Var(tail) * build.nil)
			),
			build.Var(tail)
		))
	)


def SplitKeep(operand):
	elem = types.term.Term('elem')
	tail = types.term.Term('tail')
	return scope.Scope((elem, tail),
		build.List((
			AtSuffix(
				match.Cons(operand * match.Var(elem), match.Var(tail)) *
				build.nil
			),
			build.Var(elem),
			build.Var(tail)
		))
	)


def SplitAll(operand, ):
	splitall = util.Proxy()
	splitall.subject = (
		combine.GuardedChoice(
			Split(operand),
			congruent.Cons(base.ident, project.head * splitall),
			build.List((base.ident,))
		)
	)
	return splitall


def SplitAllAfter(operand, ):
	splitall = util.Proxy()
	splitall.subject = (
		combine.GuardedChoice(
			SplitAfter(operand),
			congruent.Cons(base.ident, project.head * splitall),
			build.List((base.ident,))
		)
	)
	return splitall


def SplitAllKeep(operand, ):
	splitall = util.Proxy()
	splitall.subject = (
		combine.GuardedChoice(
			SplitKeep(operand),
			congruent.Cons(
				base.ident,
				congruent.Cons(
					base.ident,
					project.head * splitall
				)
			),
			build.List((base.ident,))
		)
	)
	return splitall
