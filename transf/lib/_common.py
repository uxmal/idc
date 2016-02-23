'''Common code for term matching, building, and congruent traversal
transformations.
'''


import aterm.factory
import aterm.term

from transf import transformation
from transf import operate
from transf.lib import base


_factory = aterm.factory.factory


class _Term(transformation.Transformation):

	def __init__(self, term):
		transformation.Transformation.__init__(self)
		assert isinstance(term, aterm.term.Term)
		self.term = term

def Term(term, _Term):
	if isinstance(term, basestring):
		term = _factory.parse(term)
	return _Term(term)


def Int(value, _Term):
	return _Term(_factory.makeInt(value))


def Real(value, _Term):
	return _Term(_factory.makeReal(value))


def Str(value, _Term):
	return _Term(_factory.makeStr(value))


def Nil(_Term):
	return _Term(_factory.makeNil())


class _Cons(transformation.Transformation):

	def __init__(self, head, tail):
		transformation.Transformation.__init__(self)
		assert isinstance(head, transformation.Transformation)
		assert isinstance(tail, transformation.Transformation)
		self.head = head
		self.tail = tail

def Cons(head, tail, _Cons, _Term):
	if head is None:
		head = base.ident
	if tail is None:
		tail = base.ident
	if type(head) is _Term and type(tail) is _Term:
		return _Term(_factory.makeCons(head.term, tail.term))
	return _Cons(head, tail)


def List(elms, tail, Cons, nil):
	if tail is None:
		tail = nil
	return operate.Nary(iter(elms), Cons, tail)


class Appl(transformation.Transformation):

	def __init__(self, name, args):
		transformation.Transformation.__init__(self)
		assert isinstance(name, basestring)
		self.name = name
		self.args = tuple(args)


class ApplCons(transformation.Transformation):

	def __init__(self, name, args):
		transformation.Transformation.__init__(self)
		assert isinstance(name, transformation.Transformation)
		assert isinstance(args, transformation.Transformation)
		self.name = name
		self.args = args


class Annos(transformation.Transformation):

	def __init__(self, annos):
		transformation.Transformation.__init__(self)
		self.annos = annos
