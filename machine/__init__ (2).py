'''Machine description.'''


class Machine:
	'''Base class for all machines.'''

	# XXX: this is largely incomplete

	def __init__(self):
		pass

	def load(self, factory, fp):
		'''Load an assembly file into a low-level IR aterm.'''
		raise NotImplementedError

	def translate(self, term):
		'''Translate the "Asm" terms into the higher-level IR equivalent
		constructs.'''
		raise NotImplementedError
