'''Term projecting transformations.'''


import aterm.project

from transf import exception
from transf import transformation
from transf import util
from transf.lib import combine


class Head(transformation.Transformation):

	def apply(self, trm, ctx):
		try:
			return trm.head
		except AttributeError:
			raise exception.Failure("not a list construction term", trm)

head = Head()


class Tail(transformation.Transformation):

	def apply(self, trm, ctx):
		try:
			return trm.tail
		except AttributeError:
			raise exception.Failure("not a list construction term", trm)

tail = Tail()


first  = head
second = combine.Composition(tail, first)
third  = combine.Composition(tail, second)
fourth = combine.Composition(tail, third)


def Nth(n):
	if n > 1:
		nth = Tail()
		for i in range(2, n):
			nth = nth * tail
		nth = nth * head
	elif n < 1:
		raise ValueError
	else: # n = 1
		n = head


class Name(transformation.Transformation):

	def apply(self, trm, ctx):
		try:
			name = trm.name
		except AttributeError:
			raise exception.Failure("not an application term", trm)
		else:
			return trm.factory.makeStr(name)

name = Name()


class Args(transformation.Transformation):

	def apply(self, trm, ctx):
		if not aterm.types.isAppl(trm):
			raise exception.Failure("not an application term", trm)
		return trm.factory.makeList(trm.args)

args = Args()


class Subterms(transformation.Transformation):

	def apply(self, trm, ctx):
		return aterm.project.subterms(trm)

subterms = Subterms()


class Annos(transformation.Transformation):

	def apply(self, trm, ctx):
		return aterm.project.annotations(trm)

annos = Annos()

