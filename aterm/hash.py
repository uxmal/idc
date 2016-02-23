'''Term hash computation.'''


from aterm import visitor


class _StructuralHash(visitor.Visitor):

	# TODO: use a more efficient hash function

	def visitTerm(self, term):
		assert False

	def visitLit(self, term):
		return hash((
			term.type,
			term.value
		))

	def visitNil(self, term):
		return hash((
			term.type,
		))

	def visitCons(self, term):
		return hash((
			term.type,
			self.visit(term.head),
			self.visit(term.tail),
		))

	def visitAppl(self, term):
		return hash((
			term.type,
			term.name,
			term.args,
		))

def structuralHash(term):
	'''Perform hashing without considering annotations.'''
	visitor = _StructuralHash()
	return visitor.visit(term)


class _FullHash(_StructuralHash):

	def visitAppl(self, term):
		term_hash = _StructuralHash.visitAppl(self, term)
		if term.annotations:
			annos_hash = structuralHash(term.annotations)
			return hash(term_hash, annos_hash)
		else:
			return term_hash

def fullHash(term):
	'''Full hash.'''
	visitor = _FullHash()
	return visitor.visit(term)
