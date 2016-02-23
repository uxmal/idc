'''Term visiting.'''


class Visitor(object):
	'''Base class for term visitors.'''

	def __init__(self):
		pass

	def visit(self, term, *args, **kargs):
		'''Visit the given term.'''
		return term.accept(self, *args, **kargs)

	def visitTerm(self, term, *args, **kargs):
		raise NotImplementedError

	def visitLit(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitInt(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitReal(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitStr(self, term, *args, **kargs):
		return self.visitLit(term, *args, **kargs)

	def visitList(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitNil(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitCons(self, term, *args, **kargs):
		return self.visitList(term, *args, **kargs)

	def visitAppl(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)


class IncrementalVisitor(Visitor):
	'''Base class for visitors which incrementally build-up a modified term.'''

	def visitHead(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitTail(self, term, *args, **kargs):
		return self.visitTerm(term, *args, **kargs)

	def visitCons(self, term, *args, **kargs):
		old_head = term.head
		old_tail = term.tail
		new_head = self.visitHead(old_head, *args, **kargs)
		new_tail = self.visitTail(old_tail, *args, **kargs)
		if new_head is not old_head or new_tail is not old_tail:
			return term.factory.makeCons(new_head, new_tail)
		else:
			return term

	def visitAppl(self, term, *args, **kargs):
		name = term.name
		old_args = term.args

		new_args = []
		modified = False
		for old_arg in old_args:
			new_arg = self.visit(old_arg, *args, **kargs)
			new_args.append(new_arg)
			modified = modified or new_arg is not old_arg

		if modified:
			return term.factory.makeAppl(
				name,
				new_args,
				term.annotations
			)
		else:
			return term
