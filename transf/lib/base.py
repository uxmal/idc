'''Base transformation classes.'''


from transf import exception
from transf import transformation


class Ident(transformation.Transformation):
	'''Identity transformation. Always returns the input term unaltered.'''

	def apply(self, trm, ctx):
		return trm

id = ident = Ident()


class Fail(transformation.Transformation):
	'''Failure transformation. Always raises an L{exception.Failure}.'''

	def apply(self, trm, ctx):
		raise exception.Failure

fail = Fail()

