'''Term projection.'''


from aterm.factory import factory
from aterm import visitor


class _Subterms(visitor.Visitor):

	def visitTerm(self, term):
		assert False

	def visitLit(self, term):
		return factory.makeNil()

	def visitList(self, term):
		return term

	def visitAppl(self, term):
		return factory.makeList(term.args)

def subterms(term):
	'''Project the direct subterms of a term.'''
	return _Subterms().visit(term)


class _Subterm(visitor.Visitor):

	def visitTerm(self, term, index):
		raise IndexError('index out of bounds')

	def visitCons(self, term, index):
		if index == 0:
			return term.head
		else:
			return self.visit(term.tail, index - 1)

	def visitAppl(self, term, index):
		return term.args[index]

def subterm(term, index):
	'''Project a direct subterm of a term.'''
	return _Subterm().visit(term, index)


class _Annotations(visitor.Visitor):

	def visitTerm(self, term):
		return term.factory.makeNil()

	def visitAppl(self, term):
		return term.annotations

def annotations(term):
	'''Project the annotations of a term.'''
	return _Annotations().visit(term)