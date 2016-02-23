'''Dot writing.'''


from aterm import walker


class Writer(walker.Walker):
	'''Walker which writes dot in aterm to a file stream.'''

	def __init__(self, fp):
		walker.Walker.__init__(self)
		self.fp = fp
	
	def write(self, dot):
		self.writeGraph(*dot.args)
	
	def writeGraph(self, nodes):
		self.fp.write("digraph {\n")
		for node in nodes:
			self.writeNode(*node.args)
		for node in nodes:
			self.writeNodeEdges(*node.args)
		self.fp.write("}")
		
	def writeNode(self, id, attrs, edges):
		self.writeId(id)
		self.writeAttrs(attrs)
		self.fp.write('\n')

	def writeNodeEdges(self, src, attrs, edges):
		for edge in edges:
			self.writeEdge(src, *edge.args)

	def writeEdge(self, src, dst, attrs):
		self.writeId(src)
		self.fp.write('->')
		self.writeId(dst)
		self.writeAttrs(attrs)
		self.fp.write('\n')

	def writeAttrs(self, attrs):
		self.fp.write('[')
		sep = ''
		for attr in attrs:
			self.fp.write(sep)
			self.writeAttr(*attr.args)
			sep = ','
		self.fp.write(']')
		
	def writeAttr(self, name, value):
		self.writeId(name)
		self.fp.write('=')
		self.writeId(value)
	
	def writeId(self, id):
		self.fp.write(str(id.value))
		

def write(dot, fp):
	'''Write the dot in aterm to a file stream.'''
	writer = Writer(fp)
	writer.write(dot)
	

def stringify(dot):
	'''Convert the dot in aterm to a string.'''
	try:
		from cStringIO import StringIO
	except ImportError:
		from StringIO import StringIO
	fp = StringIO()
	write(dot, fp)
	return fp.getvalue()	

