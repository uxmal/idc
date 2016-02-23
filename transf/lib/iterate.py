'''Transformations for iterating terms.'''


from transf import exception
from transf import operate
from transf import util


class Repeat(operate.Unary):
	'''Applies a transformation until it fails.'''

	def apply(self, trm, ctx):
		try:
			while True:
				trm = self.operand(trm, ctx)
		except exception.Failure:
			return trm


def Rec(Def):
	'''Recursive transformation.

	@param Def: transformation factory whose single argument is its own definition.
	'''
	rec = util.Proxy()
	rec.subject = Def(rec)
	return rec
