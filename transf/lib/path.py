'''Path transformations.

A path is a term comprehending a list of integer indexes which indicate the
position of a term relative to the root term. The indexes are listed orderly
from the leaves to the root.
'''


import aterm.factory
import aterm.convert
import aterm.lists
import aterm.project
import aterm.path

from transf import exception
from transf import transformation
from transf import operate
from transf.lib import base
from transf.lib import combine
from transf.lib import match
from transf.lib import build
from transf.lib import project
from transf.lib import annotation


_factory = aterm.factory.factory


get = combine.Composition(
	annotation.Get(match.ApplName('Path')),
	combine.Composition(project.args, project.first)
)


class Annotate(transformation.Transformation):
	'''Transformation which annotates the path of terms and subterms for which the
	supplied transformation succeeds.'''

	def __init__(self, operand = None, root = None):
		transformation.Transformation.__init__(self)
		if operand is None:
			self.operand = base.ident
		else:
			self.operand = operand
		if root is None:
			self.root = build.nil
		elif isinstance(root, aterm.term.Term):
			self.root = build.Term(root)
		else:
			self.root = root

	def apply(self, term, ctx):
		root = self.root.apply(term, ctx)
		def func(term):
			try:
				self.operand.apply(term, ctx)
			except exception.Failure:
				return False
			else:
				return True
		return aterm.path.annotate(term, root, func)

annotate = Annotate(base.ident, build.nil)


class _DeAnnotate(transformation.Transformation):

	def apply(self, term, ctx):
		return aterm.path.deannotate(term)

deannotate = _DeAnnotate()


class Project(transformation.Transformation):
	'''Projects a subterm along a path.'''

	def __init__(self, path):
		transformation.Transformation.__init__(self)
		if isinstance(path, aterm.term.Term):
			self.path = build.Term(path)
		else:
			self.path = path

	def apply(self, term, ctx):
		path = aterm.path.Path.fromTerm(self.path.apply(term, ctx))
		return path.project(term)


class SubTerm(transformation.Transformation):
	'''Projects a subterm along a path.'''

	def __init__(self, operand, path):
		transformation.Transformation.__init__(self)
		self.operand = operand
		if isinstance(path, aterm.term.Term):
			self.path = build.Term(path)
		else:
			self.path = path

	def apply(self, term, ctx):
		path = aterm.path.Path.fromTerm(self.path.apply(term, ctx))
		func = lambda term: self.operand.apply(term, ctx)
		return path.transform(term, func)


class Range(transformation.Transformation):
	'''Apply a transformation on a subterm range.'''

	def __init__(self, operand, start, end):
		'''Start and end indexes specify the subterms that will be transformed,
		inclusively.
		'''
		transformation.Transformation.__init__(self)
		self.operand = operand
		if start > end:
			raise ValueError('start index %r greater than end index %r' % (start, end))
		self.start = start
		self.end = end

	def apply(self, term, ctx):
		head, rest = aterm.lists.split(term, self.start)
		old_body, tail = aterm.lists.split(rest, self.end - self.start)

		new_body = self.operand.apply(old_body, ctx)
		if new_body is not old_body:
			return head.extend(new_body.extend(tail))
		else:
			return term


def PathRange(operand, start, end):
	'''Apply a transformation on a path range. The tails of the start and end
	aterm.path should be equal.'''
	result = operand
	result = Range(result, start[0], end[0])
	if start[1:] != end[1]:
		raise ValueError('start and end path tails differ: %r, %r' % start, end)
	result = SubTerm(result, start)
	return result


class Equals(operate.Unary):

	def apply(self, term, ctx):
		ref = self.operand.apply(term, ctx)
		pTerm = aterm.path.Path.fromTerm(term)
		pRef = aterm.path.Path.fromTerm(ref)
		if pTerm.equals(pRef):
			return term
		else:
			raise exception.Failure


class Contains(operate.Unary):

	def apply(self, term, ctx):
		ref = self.operand.apply(term, ctx)
		pTerm = aterm.path.Path.fromTerm(term)
		pRef = aterm.path.Path.fromTerm(ref)
		if pTerm.contains(pRef):
			return term
		else:
			raise exception.Failure


class Contained(operate.Unary):

	def apply(self, term, ctx):
		ref = self.operand.apply(term, ctx)
		pTerm = aterm.path.Path.fromTerm(term)
		pRef = aterm.path.Path.fromTerm(ref)
		if pTerm.contained(pRef):
			return term
		else:
			raise exception.Failure

