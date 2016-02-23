'''Exception class hierarchy.'''


class BaseException(Exception):
	'''Base class for all term-related exceptions.'''
	pass

	# TODO: have all raised exceptions derived from this


class ParseError(BaseException):
	'''Error parsing textual representation of terms.'''
	pass
