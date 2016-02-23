'''Term comparison.'''


from aterm import types
from aterm import visitor


class _Comparator(visitor.Visitor):
	'''Base class for term comparators.'''

	def visitTerm(self, term):
		assert False

	def visitLit(self, term, other):
		return \
			term.type == other.type and \
			term.value == other.value

	def visitNil(self, term, other):
		return \
			types.NIL == other.type

	def visitCons(self, term, other):
		return \
			types.CONS == other.type and \
			self.visit(term.head, other.head) and \
			self.visit(term.tail, other.tail)

	def visitAppl(self, term, other):
		if types.APPL != other.type:
			return False
		if term.name != other.name:
			return False
		if len(term.args) != len(other.args):
			return False
		for term_arg, other_arg in zip(term.args, other.args):
			if not self.visit(term_arg, other_arg):
				return False
		return True


class _EquivalenceComparator(_Comparator):
	'''Comparator for determining term equivalence, which does not
	consider annotations.'''

	def visit(self, term, other):
		return \
			term is other or \
			_Comparator.visit(self, term, other)

def isEquivalent(term, other):
	'''Determines if two terms are equivalent, i.e., equal except for the
	annotations.'''
	comparator = _EquivalenceComparator()
	return comparator.visit(term, other)


class _EqualityComparator(_EquivalenceComparator):
	'''Comparator for determining term equality, which considers annotations.
	'''

	def compareAnnos(self, terms, others):
		if terms is None:
			return others is None
		else:
			return others is not None and self.visit(terms, others)

	def visitAppl(self, term, other):
		return \
			_EquivalenceComparator.visitAppl(self, term, other) and \
			self.compareAnnos(term.annotations, other.annotations)

def isEqual(term, other):
	'''Determines if two terms are equal (including annotations).'''
	comparator = _EqualityComparator()
	return comparator.visit(term, other)
