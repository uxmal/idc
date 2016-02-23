'''Hash table variable.'''


import aterm.factory

from transf import exception
from transf import context
from transf import transformation
from transf import operate
from transf import variable
#from transf.lib import base
#from transf.lib import combine
#from transf.lib import build
#from transf.lib import build
from transf.variable import Variable
from transf.variable import VariableTransformation


_factory = aterm.factory.factory


class _Table(dict):
	'''A table is mapping of terms to terms.'''

	def copy(self):
		return _Table(self)

	def add(self, other):
		self.update(other)

	def sub(self, other):
		for key in self.iterkeys():
			if key not in other:
				del self[key]

	def equals(self, other):
		if len(self) != len(other):
			return False
		for key, value in self.iteritems():
			try:
				if value != other[key]:
					return False
			except KeyError:
				return False
		return True


def _table(binding, ctx):
	tbl = binding.get(ctx)
	if tbl is None:
		tbl = _Table()
		binding.set(ctx, tbl)
	return tbl


class Table(variable.Variable):
	'''A table is mapping of terms to terms.'''

	@VariableTransformation
	def init(binding, trm, ctx):
		binding.set(ctx, _Table())

	@VariableTransformation
	def set(binding, trm, ctx):
		'''Setting a [key, value] list will add the pair to the table. Setting
		a [key] list will remove the key and its value from the table.'''
		# TODO: better exception handling
		tbl = _table(binding, ctx)
		key, val = trm
		tbl[key] = val
		return trm

	@VariableTransformation
	def unset(binding, trm, ctx):
		'''Setting a [key, value] list will add the pair to the table. Setting
		a [key] list will remove the key and its value from the table.'''
		# TODO: better exception handling
		tbl = _table(binding, ctx)
		try:
			return tbl.pop(trm)
		except KeyError:
			raise exception.Failure("term not in table", trm)
		return trm

	@VariableTransformation
	def clear(binding, trm, ctx):
		'''Clears all elements of the table.'''
		binding.set(ctx, _Table())
		return trm

	@VariableTransformation
	def match(binding, trm, ctx):
		'''Lookups the key matching the term in the table.'''
		tbl = _table(binding, ctx)
		try:
			tbl[trm]
		except KeyError:
			raise exception.Failure("term not in table", trm)
		else:
			return trm

	@VariableTransformation
	def build(binding, trm, ctx):
		'''Builds a list all keys in the table.'''
		tbl = _table(binding, ctx)
		return _factory.makeList(tbl.keys())

	@VariableTransformation
	def congruent(binding, trm, ctx):
		'''Lookups the key matching to the term in the table and return its
		associated value.
		'''
		tbl = _table(binding, ctx)
		try:
			return tbl[trm]
		except KeyError:
			raise exception.Failure("term not in table", trm)

	def Add(self, other):
		assert isinstance(other, Table)
		return Add(self.binding, other.binding)

	def Filter(self, transf):
		assert isinstance(transf, transformation.Transformation)
		return Filter(self.binding, transf)


class Add(transformation.Transformation):
	'''Adds too tables.'''

	def __init__(self, var1, var2):
		transformation.Transformation.__init__(self)
		self.var1 = var1
		self.var2 = var2

	def apply(self, trm, ctx):
		tbl1 = _table(self.var1, ctx)
		tbl2 = _table(self.var2, ctx)
		tbl1.update(tbl2)
		return trm


class Filter(transformation.Transformation):

	def __init__(self, binding, transf):
		transformation.Transformation.__init__(self)
		self.binding = binding
		self.transf = transf

	def apply(self, trm, ctx):
		tbl = _table(self.binding, ctx)
		tbl2 = _Table()
		for key, val in tbl:
			try:
				item = trm.factory.makeList([key, val])
				key, val = self.transf.apply(item, ctx)
			except exception.Failure:
				del tbl[key]
			else:
				tbl2[key] = val
		self.binding.set(ctx, tbl2)
		return trm


class Join(operate.Binary):
	'''Transformation composition which joins (unites/intersects) tables in
	the process.
	'''

	def __init__(self, loperand, roperand, uvars, ivars):
		operate.Binary.__init__(self, loperand, roperand)
		for var in zip(uvars, ivars):
			assert isinstance(var, Table)
		self.unames = [var.binding for var in uvars]
		self.inames = [var.binding for var in ivars]

	def apply(self, trm, ctx):
		# duplicate tables
		utbls = []
		itbls = []
		lvars = []
		rvars = []
		for var in self.unames:
			tbl = _table(var, ctx)
			ltbl = tbl.copy()
			lvars.append((var.name, ltbl))
			rtbl = tbl.copy()
			rvars.append((var.name, rtbl))
			utbls.append((tbl, ltbl, rtbl))
		for var in self.inames:
			tbl = _table(var, ctx)
			ltbl = tbl.copy()
			lvars.append((var.name, ltbl))
			rtbl = tbl.copy()
			rvars.append((var.name, rtbl))
			itbls.append((tbl, ltbl, rtbl))
		lctx = context.Context(lvars, ctx)
		rctx = context.Context(rvars, ctx)

		# apply transformations
		trm = self.loperand.apply(trm, lctx)
		trm = self.roperand.apply(trm, rctx)

		# join the tables
		for tbl, ltbl, rtbl in utbls:
			# unite
			tbl.clear()
			tbl.add(ltbl)
			tbl.add(rtbl)
		for tbl, ltbl, rtbl in itbls:
			# intersect
			tbl.clear()
			tbl.add(ltbl)
			tbl.sub(rtbl)

		return trm


class Iterate(operate.Unary):
	'''Transformation composition which joins (unites/intersects) tables in
	the process.
	'''

	def __init__(self, operand, uvars, ivars):
		operate.Unary.__init__(self, operand)
		self.unames = [var.binding for var in uvars]
		self.inames = [var.binding for var in ivars]

	def apply(self, trm, ctx):
		utbls = []
		itbls = []
		rvars = []
		for var in self.unames:
			tbl = _table(var, ctx)
			ltbl = tbl.copy()
			rtbl = tbl.copy()
			rvars.append((var.name, rtbl))
			utbls.append((tbl, ltbl, rtbl))
		for var in self.inames:
			tbl = _table(var, ctx)
			ltbl = tbl.copy()
			rtbl = tbl.copy()
			rvars.append((var.name, rtbl))
			itbls.append((tbl, ltbl, rtbl))
		rctx = context.Context(rvars, ctx)

		# iterate
		maxits = 10
		for i in range(maxits):
			# apply transformation
			res = self.operand.apply(trm, rctx)

			# join the tables
			equals = True
			for tbl, ltbl, rtbl in utbls:
				# unite
				equals = equals and ltbl.equals(rtbl)
				ltbl.add(rtbl)
			for tbl, ltbl, rtbl in itbls:
				# intersect
				equals = equals and ltbl.equals(rtbl)
				ltbl.sub(rtbl)
			if equals:
				break
		if i == maxits:
			raise exception.Fatal('maximum number of exceptions reached')

		# copy final result
		for tbl, ltbl, rtbl in utbls:
			tbl.clear()
			tbl.add(ltbl)
		for tbl, ltbl, rtbl in itbls:
			tbl.clear()
			tbl.add(ltbl)

		return res
