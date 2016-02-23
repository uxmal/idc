'''Term conversion.'''


from aterm import visitor


class _ToInt(visitor.Visitor):

	def visitTerm(self, term):
		raise TypeError('not an integer term', term)

	def visitInt(self, term):
		return term.value

def toInt(term):
	'''Convert an integer term to its integer value.'''
	return _ToInt().visit(term)


class _ToReal(visitor.Visitor):

	def visitTerm(self, term):
		raise TypeError('not a real term', term)

	def visitReal(self, term):
		return term.value

def toReal(term):
	'''Convert a real term to its real value.'''
	return _ToReal().visit(term)


class _ToStr(visitor.Visitor):

	def visitTerm(self, term):
		raise TypeError('not a string term', term)

	def visitStr(self, term):
		return term.value

def toStr(term):
	'''Convert a string term to its string value.'''
	return _ToStr().visit(term)


class _ToLit(visitor.Visitor):

	def visitTerm(self, term):
		raise TypeError('not a literal term', term)

	def visitLit(self, term):
		return term.value

def toLit(term):
	'''Convert a literal term to its value.'''
	return _ToLit().visit(term)


class _ToList(visitor.Visitor):

	def visitTerm(self, term):
		raise TypeError('not a list term', term)

	def visitNil(self, term):
		return []

	def visitCons(self, term):
		head = term.head
		tail = self.visit(term.tail)
		return [head] + tail

def toList(term):
	'''Convert a list term to a list of terms.'''
	return _ToList().visit(term)


class _ToObj(visitor.Visitor):

	def visitTerm(self, term):
		raise TypeError('term not convertible', term)

	def visitLit(self, term):
		return term.value

	def visitNil(self, term):
		return []

	def visitCons(self, term):
		head = self.visit(term.head)
		tail = self.visit(term.tail)
		return [head] + tail

#	def visitAppl(self, term):
#		# return application terms unmodified
#		return term

def toObj(term):
	'''Recursively convert literal and list terms to the corresponding
	Python objects.'''
	return _ToObj().visit(term)
