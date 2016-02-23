'''Exception classes.'''


class Base(Exception):
	'''Base class for all exceptions.'''

	def __str__(self):
		args = self.args
		if len(args) > 1 and isinstance(args[0], basestring): 
			return ': '.join((str(args[0]), ', '.join([str(arg) for arg in args[1:]])))
		else:
			return Exception.__str__(self)


class Failure(Base):
	'''Transformation failed to apply.'''

	pass


class Fatal(Base):
	'''Unrecoverable error during transformation.'''
	
	pass