'''Term writing.'''


from aterm import types
from aterm import visitor


class Writer(visitor.Visitor):
	'''Base class for term writers.'''

	def __init__(self, fp):
		visitor.Visitor.__init__(self)
		self.fp = fp


class TextWriter(Writer):
	'''Writes a term to a text stream.'''

	def writeList(self, seq, begin, end, sep=','):
		self.fp.write(begin)
		cursep = ""
		for term in seq:
			self.fp.write(cursep)
			self.visit(term)
			cursep = sep
		self.fp.write(end)

	def visitInt(self, term):
		self.fp.write(str(term.value))

	def visitReal(self, term):
		value = term.value
		if float(int(value)) == value:
			self.fp.write('%0.1f' % value)
		else:
			self.fp.write('%g' % value)

	def visitStr(self, term):
		s = str(term.value)
		s = s.replace('\"', '\\"')
		s = s.replace('\t', '\\t')
		s = s.replace('\r', '\\r')
		s = s.replace('\n', '\\n')
		self.fp.write('"' + s + '"')

	def visitList(self, term):
		self.writeList(term, '[', ']')

	def visitAppl(self, term):
		self.fp.write(term.name)
		args = term.args
		if term.name == '' or term.args:
			self.writeList(term.args, '(', ')')
		if term.annotations:
			self.writeList(term.annotations, '{', '}')


# TODO: implement a pretty-printer


class AbbrevTextWriter(TextWriter):
	'''Write an abbreviated term representation.'''

	def __init__(self, fp, depth):
		TextWriter.__init__(self, fp)
		self.depth = depth

	def visitList(self, term):
		if self.depth > 1:
			self.depth -= 1
			TextWriter.visitList(self, term)
			self.depth += 1
		else:
			self.fp.write('[...]')


# TODO: implement a XML writer