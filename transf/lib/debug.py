'''Debugging transformations.'''


import sys
import traceback
import inspect
import os.path
import time
import unittest

import aterm.term

from transf import exception
from transf import transformation
from transf import context
from transf import operate
from transf import util


log = sys.stderr


#############################################################################
# Automatically start the debugger on an exception.
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65287

def excepthook(type, value, tb):

	if hasattr(sys, 'ps1') \
	or not (sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()) \
	or type == SyntaxError or type == KeyboardInterrupt:
		# we are in interactive mode or we don't have a tty-like
		# device, so we call the default hook
		oldexcepthook(type, value, tb)
	else:
		import traceback, pdb
		# we are NOT in interactive mode, print the exception...
		traceback.print_exception(type, value, tb)
		print
		# ...then start the debugger in post-mortem mode.
		pdb.pm()

if 0:
	oldexcepthook, sys.excepthook = sys.excepthook, excepthook


class DebugMixin(object):

	def dump_line(self, filename, lineno):
		log.write('  File "%s", line %d\n' % (filename, lineno))

	def dump_term(self, term):
		log.write('    term = %r\n' % term)

	def dump_context(self, ctx):
		log.write('    ctx = {')
		sep = ''
		for name, var in ctx:
			sep = '\n    '
			log.write('\n      %r: %r,' % (name, var))
		log.write(sep + '}\n')


class Log(transformation.Transformation):
	'''Log message.'''

	def __init__(self, msg, *args):
		transformation.Transformation.__init__(self)
		self.msg = msg
		self.args = args

	def apply(self, trm, ctx):
		args = []
		for arg in self.args:
			try:
				res = arg.apply(trm, ctx)
			except exception.Failure:
				res = '<Failure>'
			else:
				res = str(res)
			args.append(res)
		# TODO: better error handling
		msg = self.msg % tuple(args)
		log.write(msg)
		return trm


class Dump(transformation.Transformation, DebugMixin):
	'''Dump the current term and context.'''

	def __init__(self):
		transformation.Transformation.__init__(self)
		try:
			caller = inspect.currentframe().f_back
			self.filename = os.path.basename(caller.f_code.co_filename)
			self.lineno = caller.f_lineno
		finally:
			del caller

	def apply(self, term, ctx):
		self.dump_line(self.filename, self.lineno)
		self.dump_term(term)
		self.dump_context(ctx)
		return term


class Trace(util.Proxy, DebugMixin):
	'''Trace the operand transformation transformation.'''

	def __init__(self, operand=None, name=None):
		util.Proxy.__init__(self, operand)
		self.time = False
		self.name = name

	def apply(self, term, ctx):
		log.write('=> %20s: %r\n' % (self.name, term))
		try:
			try:
				start = time.clock()
				try:
					term = self.subject.apply(term, ctx)
				finally:
					end = time.clock()
			except Exception, ex:
				result = '<%s %s>' % (ex.__class__.__name__, ex)
				raise
			else:
				result = repr(term)
				return term
		finally:
			delta = end - start
			#log.write('<= %20s (%.03fs): %s\n' % (self.name, delta, result))
			log.write('<= %20s: %s\n' % (self.name, result))


class Traceback(operate.Unary, DebugMixin):

	def __init__(self, operand):
		operate.Unary.__init__(self, operand)

	def apply(self, term, ctx):
		try:
			return self.operand.apply(term, ctx)
		except exception.Failure:
			e_type, e_value, tb = sys.exc_info()
			records = inspect.getinnerframes(tb, 0)
			for frame, file, lineno, func, lines, index in records:
				file = file and os.path.abspath(file) or '?'
				args, varargs, varkw, locals = inspect.getargvalues(frame)
				print locals['self'].__class__.__name__,
				self.dump_line(file, lineno)
				try:
					self.dump_term(locals['term'])
				except:
					pass
				try:
					self.dump_context(locals['ctx'])
				except:
					pass
			raise


class TestCase(transformation.Transformation):
	'''A test case based on a transformation.'''

	def __init__(self, input, transf, expectedOutput):
		transformation.Transformation.__init__(self)
		self._input = input
		self._transf = transf
		self._expectedOutput = expectedOutput

	def apply(self, trm, ctx):
		input = self._input.apply(trm, ctx)
		expectedOutput = self._expectedOutput.apply(trm, ctx)
		output = self._transf.apply(input, ctx)
		if not expectedOutput.isEquivalent(output):
			# TODO: use diff lib
			sys.stderr.write("%s\n" % expectedOutput)
			sys.stderr.write("%s\n" % output)
			raise AssertionError("%s -> %s (!= %s)" %(input, output, expectedOutput))
		return output

	def runTest(self):
		trm = aterm.factory.factory.makeStr("Ignored")
		ctx = context.Context()
		self.apply(trm, ctx)


