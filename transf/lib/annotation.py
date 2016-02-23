'''High-level annotation transformations.'''


import aterm.annotation

from transf import operate
from transf.lib import combine
from transf.lib import congruent
from transf.lib import project
from transf.lib import lists


class Set(operate.Unary):

	def apply(self, trm, ctx):
		anno = self.operand.apply(trm, ctx)
		return aterm.annotation.set(trm, anno)


def Get(label):
	return combine.Composition(project.annos, lists.Fetch(label))


def Has(label):
	return combine.Where(Get(label))


def Del(label):
	return congruent.Annos(lists.Filter(combine.Not(label)))
