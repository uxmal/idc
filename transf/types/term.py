'''Term variables.'''


from transf import exception
from transf.variable import Variable
from transf.variable import VariableTransformation


class Term(Variable):

	@VariableTransformation
	def init(binding, trm, ctx):
		binding.set(ctx, None)
		return trm

	@VariableTransformation
	def assign(binding, trm, ctx):
		binding.set(ctx, trm)
		return trm

	@VariableTransformation
	def clear(binding, trm, ctx):
		binding.set(ctx, None)
		return trm

	@VariableTransformation
	def match(binding, trm, ctx):
		'''Match the term against this variable value, setting it,
		if it is undefined.'''
		old = binding.get(ctx)
		if old is None:
			binding.set(ctx, trm)
		elif old != trm:
			raise exception.Failure('variable mismatch', binding.name, trm, old)
		return trm

	@VariableTransformation
	def build(binding, trm, ctx):
		'''Returns this variable term, if defined.'''
		trm = binding.get(ctx)
		if trm is None:
			raise exception.Failure('undefined variable', binding.name)
		return trm

	congruent = match

