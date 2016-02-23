'''Term class hierarchy.'''


# pylint: disable-msg=W0142


from aterm import types
from aterm import compare
from aterm import hash
from aterm import write
from aterm import lists


class Term(object):
	'''Base class for all terms.

	Terms are non-modifiable. Changes are carried out by returning another term
	instance.
	'''

	# NOTE: most methods defer the execution to visitors

	__slots__ = ['factory']

	def __init__(self, factory):
		self.factory = factory

	# XXX: this has a large inpact in performance
	if __debug__ and False:
		def __setattr__(self, name, value):
			'''Prevent modification of term attributes.'''

			# TODO: implement this with a metaclass

			try:
				object.__getattribute__(self, name)
			except AttributeError:
				object.__setattr__(self, name, value)
			else:
				raise AttributeError("attempt to modify read-only term attribute '%s'" % name)

	def __delattr__(self, name):
		'''Prevent deletion of term attributes.'''
		raise AttributeError("attempt to delete read-only term attribute '%s'" % name)

	def getType(self):
		'''Gets the type of this term.'''
		return self.type

	def getHash(self):
		'''Generate a hash value for this term.'''
		return hash.fullHash(self)

	def getStructuralHash(self):
		'''Generate a hash value for this term.
		Annotations are not taken into account.
		'''
		return hash.structuralHash(self)

	__hash__ = getStructuralHash

	def isEquivalent(self, other):
		'''Checks for structural equivalence of this term agains another term.'''
		return compare.isEquivalent(self, other)

	def isEqual(self, other):
		'''Checks equality of this term against another term.  Note that for two
		terms to be equal, any annotations they might have must be equal as
		well.'''
		return compare.isEqual(self, other)

	def __eq__(self, other):
		if not isinstance(other, Term):
			# TODO: produce a warning
			return False
		return compare.isEquivalent(self, other)

	def __ne__(self, other):
		return not self.__eq__(other)

	def rmatch(self, other):
		'''Matches this term against a string pattern.'''
		return self.factory.match(other, self)

	def accept(self, visitor, *args, **kargs):
		'''Accept a visitor.'''
		raise NotImplementedError

	def writeToTextFile(self, fp):
		'''Write this term to a file object.'''
		writer = write.TextWriter(fp)
		writer.visit(self)

	def __str__(self):
		'''Get the string representation of this term.'''
		try:
			from cStringIO import StringIO
		except ImportError:
			from StringIO import StringIO
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()

	def __repr__(self):
		try:
			from cStringIO import StringIO
		except ImportError:
			from StringIO import StringIO
		fp = StringIO()
		writer = write.AbbrevTextWriter(fp, 3)
		try:
			writer.visit(self)
		except:
			fp.write('...<error>')
		return '<Term %s>' % (fp.getvalue(),)


class Lit(Term):
	'''Base class for literal terms.'''

	__slots__ = ['value']

	def __init__(self, factory, value):
		Term.__init__(self, factory)
		self.value = value

	def getValue(self):
		return self.value


class Integer(Lit):
	'''Integer literal term.'''

	__slots__ = []

	type = types.INT

	def __init__(self, factory, value):
		if not isinstance(value, (int, long)):
			raise TypeError('value is not an integer', value)
		Lit.__init__(self, factory, value)

	def __int__(self):
		return int(self.value)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitInt(self, *args, **kargs)


class Real(Lit):
	'''Real literal term.'''

	__slots__ = []

	type = types.REAL

	def __init__(self, factory, value):
		if not isinstance(value, float):
			raise TypeError('value is not a float', value)
		Lit.__init__(self, factory, value)

	def __float__(self):
		return float(self.value)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitReal(self, *args, **kargs)


class Str(Lit):
	'''String literal term.'''

	__slots__ = []

	type = types.STR

	def __init__(self, factory, value):
		if not isinstance(value, str):
			raise TypeError('value is not a string', value)
		Lit.__init__(self, factory, value)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitStr(self, *args, **kargs)


class List(Term):
	'''Base class for list terms.'''

	__slots__ = []

	# Python's list compatability methods

	def __nonzero__(self):
		return not lists.empty(self)

	def __len__(self):
		return lists.length(self)

	def __getitem__(self, index):
		return lists.item(self, index)

	def __iter__(self):
		return lists.Iter(self)

	def insert(self, index, element):
		return lists.insert(self, index, element)

	def append(self, element):
		return lists.append(self, element)

	def extend(self, other):
		return lists.extend(self, other)

	def reverse(self):
		return lists.reverse(self)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitList(self, *args, **kargs)


class Nil(List):
	'''Empty list term.'''

	__slots__ = []

	type = types.NIL

	def __init__(self, factory):
		List.__init__(self, factory)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitNil(self, *args, **kargs)


class Cons(List):
	'''Concatenated list term.'''

	__slots__ = ['head', 'tail']

	type = types.CONS

	def __init__(self, factory, head, tail):
		List.__init__(self, factory)
		if not isinstance(head, Term):
			raise TypeError("head is not a term", head)
		self.head = head
		if not isinstance(tail, List):
			raise TypeError("tail is not a list term", tail)
		self.tail = tail

	def accept(self, visitor, *args, **kargs):
		return visitor.visitCons(self, *args, **kargs)


class Appl(Term):
	'''Application term.'''

	__slots__ = ['name', 'args', 'annotations']

	type = types.APPL

	def __init__(self, factory, name, args, annotations):
		Term.__init__(self, factory)
		if not isinstance(name, basestring):
			raise TypeError("name is not a string", name)
		self.name = name
		self.args = tuple(args)
		for arg in self.args:
			if not isinstance(arg, Term):
				raise TypeError("arg is not a term", arg)
		if not isinstance(annotations, List):
			raise TypeError("annotations is not a list", annotations)
		self.annotations = annotations

	def getArity(self):
		return len(self.args)

	def setAnnotations(self, annotations):
		'''Return a copy of this term with the given annotations.'''
		return self.factory.makeAppl(self.name, self.args, annotations)

	def removeAnnotations(self):
		'''Return a copy of this term with all annotations removed.'''
		return self.factory.makeAppl(self.name, self.args)

	def accept(self, visitor, *args, **kargs):
		return visitor.visitAppl(self, *args, **kargs)

