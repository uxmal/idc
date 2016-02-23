'''List term operations.'''


from aterm import types
from aterm import visitor


def empty(term):
	'''Whether a list term is empty or not.'''
	return types.isNil(term)


def length(term):
	'''Length of a list term.'''
	length = 0
	while not types.isNil(term):
		assert types.isCons(term)
		length += 1
		term = term.tail
	return length


def item(term, index):
	'''Get item at given index of a list term.'''
	if index < 0:
		raise IndexError('index out of bounds')
	while True:
		if types.isNil(term):
			raise IndexError('index out of bounds')
		if not types.isCons(term):
			raise TypeError('not a list term', term)
		if index == 0:
			return term.head
		index -= 1
		term = term.tail


class Iter(visitor.Visitor):
	'''List term iterator.'''

	def __init__(self, term):
		visitor.Visitor.__init__(self)
		self.term = term

	def next(self):
		return self.visit(self.term)

	def visitTerm(self, term):
		raise TypeError('not a list term', term)

	def visitNil(self, term):
		raise StopIteration

	def visitCons(self, term):
		head = term.head
		self.term = term.tail
		return head


def extend(head, tail):
	'''Return the concatenation of two list terms.'''
	if types.isNil(head):
		return tail
	if types.isNil(tail):
		return head
	factory = tail.factory
	for elm in reversed(head):
		tail = factory.makeCons(elm, tail)
	return tail


def append(head, tail):
	'''Append an element to a list.'''
	factory = tail.factory
	return extend(head, factory.makeCons(other, factory.makeNil()))


def insert(term, index, other):
	'''Insert an element into the list.'''
	factory = term.factory
	accum = []
	for i in range(index):
		accum.append(term.head)
		term = term.tail
	term = factory.makeCons(other, term)
	for elem in reversed(accum):
		term = factory.makeCons(elem, term)
	return term


def reverse(term):
	'''Reverse a list term.'''
	factory = term.factory
	accum = factory.makeNil()
	for elm in term:
		accum = factory.makeCons(elm, accum)
	return accum


def map(function, term):
	"""Return a list term with the elements for transformed by the function."""
	return term.factory.makeList([function(elem) for elem in term])


def rmap(function, term):
	"""Return a list term with the elements for transformed by the function."""
	factory = term.factory
	accum = factory.makeNil()
	for elem in reversed(list(term)):
		accum = factory.makeCons(function(elem), accum)
	return accum


def filter(function, term):
	"""Return a list term with the elements for which the function returns
	true."""
	return term.factory.makeList([elem for elem in term if function(elem)])


def fetch(function, term):
	"""Return a the first term of a list term for which the function returns
	true."""
	for elm in term:
		if function(elm):
			return elm
	return None


def split(term, index):
	'''Splits a list term in two lists.
	The argument is the index of the first element of the second list.
	'''
	factory = term.factory
	head = []
	for i in range(index):
		head.append(term.head)
		term = term.tail
	return factory.makeList(head), term
