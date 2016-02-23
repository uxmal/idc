'''Congruent term transformations.'''


import aterm.types

from transf import exception
from transf import transformation
from transf import variable
from transf import operate
from transf.lib import base
from transf.lib import combine
from transf.lib import _common
from transf.lib import match


class _ConsL(_common._Cons):

	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list cons term', term)

		new_head = self.head.apply(old_head, ctx)
		new_tail = self.tail.apply(old_tail, ctx)

		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(new_head, new_tail)
		else:
			return term

def ConsL(head, tail):
	return _common.Cons(head, tail, _ConsL, match._Term)


class _ConsR(_common._Cons):

	def apply(self, term, ctx):
		try:
			old_head = term.head
			old_tail = term.tail
		except AttributeError:
			raise exception.Failure('not a list cons term', term)

		new_tail = self.tail.apply(old_tail, ctx)
		new_head = self.head.apply(old_head, ctx)

		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(new_head, new_tail)
		else:
			return term

def ConsR(head, tail):
	return _common.Cons(head, tail, _ConsR, match._Term)


Cons = ConsL


def List(elms, tail = None):
	return _common.List(elms, tail, Cons, match.nil)


class Appl(_common.Appl):
	'''Traverse a term application.'''

	def apply(self, term, ctx):
		try:
			name = term.name
			old_args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)

		if name != self.name:
			raise exception.Failure

		if len(self.args) != len(old_args):
			raise exception.Failure

		new_args = []
		modified = False
		for self_arg, old_arg in zip(self.args, old_args):
			new_arg = self_arg.apply(old_arg, ctx)
			new_args.append(new_arg)
			modified = modified or new_arg is not old_arg

		if modified:
			return term.factory.makeAppl(
				name,
				new_args,
				term.annotations
			)
		else:
			return term

class ApplCons(_common.ApplCons):
	'''Traverse a term application.'''

	def apply(self, term, ctx):
		try:
			old_name = term.name
			old_args = term.args
		except AttributeError:
			raise exception.Failure('not an application term', term)

		factory = term.factory
		old_name = factory.makeStr(old_name)
		old_args = factory.makeList(old_args)
		new_name = self.name.apply(old_name, ctx)
		new_args = self.args.apply(old_args, ctx)

		if new_name is not old_name or new_args is not old_args:
			new_name = new_name.value
			new_args = tuple(new_args)
			return term.factory.makeAppl(
				new_name,
				new_args,
				term.annotations
			)
		else:
			return term


def Var(var):
	assert isinstance(var, variable.Variable)
	return var.congruent


class Annos(_common.Annos):

	def apply(self, term, ctx):
		if aterm.types.isAppl(term):
			annos = self.annos.apply(term.annotations, ctx)
			if annos is not term.annotations:
				return term.factory.makeAppl(term.name, term.args, annos)
		return term


def Anno(anno):
	from transf.lib.traverse import One
	return Annos(One(anno))


class Subterms(transformation.Transformation):
	'''Congruent transformation of subterms.'''

	def __init__(self, children, leaf):
		'''
		@param children: transformation to be applied to the term children.
		@param leaf: transformation to be applied if the term has no children.
		'''
		transformation.Transformation.__init__(self)
		self.leaf = leaf
		self.list = children
		self.appl = ApplCons(base.ident, children)

	def apply(self, term, ctx):
		if aterm.types.isAppl(term):
			return self.appl.apply(term, ctx)
		elif aterm.types.isList(term):
			return self.list.apply(term, ctx)
		else:
			return self.leaf.apply(term, ctx)

