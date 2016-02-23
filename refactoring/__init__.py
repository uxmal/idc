"""Classes for modelling and applying refactories."""


import os
import sys
import unittest

import aterm.path
import transf.exception


class Refactoring:
	"""Abstract base class for refactorings."""

	def __init__(self):
		pass

	def name(self):
		"""Rerturn a description of this refactoring. Used for persistency,
		roolback, etc."""
		raise NotImplementedError

	def applicable(self, term, selection):
		"""Verifies the pre-conditions for applying this refactory are met."""
		raise NotImplementedError

	def input(self, term, selection):
		"""Ask user input. It should return a list of arguments."""
		raise NotImplementedError

	def apply(self, term, args):
		"""Apply the refactory."""
		raise NotImplementedError


class ModuleRefactoring(Refactoring):
	'''A refactoring that lives in a module of its own.'''

	def __init__(self, module):
		self.module = module
		try:
			self._applicable = self.module.applicable
			self._input = self.module.input
			self._apply = self.module.apply
		except AttributeError:
			raise ValueError("not a refactoring module %s", module.__name__)

	def name(self):
		return self.module.__doc__

	def _selection(self, selection):
		start, end = selection
		start = aterm.path.Path.fromTerm(start)
		end = aterm.path.Path.fromTerm(end)
		selection = start.ancestor(end)
		return selection.toTerm()

	def applicable(self, trm, selection):
		factory = trm.factory
		selection = self._selection(selection)
		ctx = transf.context.Context()
		trm = factory.makeList([trm, selection])
		try:
			self._applicable.apply(trm, ctx)
		except transf.exception.Failure:
			return False
		else:
			return True

	def input(self, trm, selection):
		factory = trm.factory
		selection = self._selection(selection)
		ctx = transf.context.Context()
		trm = factory.makeList([trm, selection])
		args = self._input.apply(trm, ctx)
		return args

	def apply(self, trm, args):
		factory = trm.factory
		ctx = transf.context.Context()
		trm = factory.makeList([trm, args])
		try:
			return self._apply.apply(trm, ctx)
		except transf.exception.Failure, ex:
			raise
			return trm


class Factory:
	"""Factory for refactories."""

	def __init__(self):
		"""Initialize the factory, populating with the list of known
		refactorings.
		"""
		self.load()

	def load(self):
		self.refactorings = {}
		for path in __path__:
			for name in os.listdir(path):
				name, ext = os.path.splitext(name)
				if name != '__init__' and ext == '.py':
					fullname = __name__ + '.' + name
					loaded = fullname in sys.modules
					module = __import__(fullname)
					module = getattr(module, name)
					if loaded:
						try:
							reload(module)
						except ImportError:
							# XXX: misterous error on Python 2.4
							pass
					try:
						refactoring = ModuleRefactoring(module)
					except ValueError:
						pass
					else:
						self.refactorings[refactoring.name()] = refactoring

	def applicables(self, term, selection):
		"""Enumerate the applicable refactorings to the given term and
		selection context.
		"""
		for refactoring in self.refactorings.itervalues():
			if refactoring.applicable(term, selection):
				yield refactoring
		raise StopIteration

	def from_name(self, name):
		"""Return the refactoring with the specified name."""
		return self.refactorings[name]

