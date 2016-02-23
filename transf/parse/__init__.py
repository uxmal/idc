'''Transformation parsing.'''


import sys
import inspect

import antlr
from antlraterm import Walker as Converter

from transf.parse.lexer import Lexer
from transf.parse.parser import Parser
from transf.parse.compiler import Compiler


def _parse(buf, production="definitions", debug=False):
	'''Generate a parser for a string buffer.'''
	lexer = Lexer(buf)
	parser = Parser(lexer, debug=debug)
	try:
		ast = getattr(parser, production)()
		ast = parser.getAST()
		converter = Converter()
		term = converter.aterm(ast)
	except antlr.RecognitionException, ex:
		parser.reportError(ex)
		if ex.line != -1:
			lines = buf.split("\n")
			line = lines[ex.line - 1]

			frame = sys._getframe(3)
			filename = frame.f_code.co_filename
			name = frame.f_code.co_name
			try:
				lines = open(filename, "rt").read().split("\n")
				try:
					lineno = lines.index(line) + 1
				except ValueError:
					lineno = frame.f_lineno
			except:
				lineno = ex.line
			sys.stderr.write('  File "%s", line %d, in %s\n' % (filename, lineno, name))
			sys.stderr.write(line.expandtabs() + "\n")
			if ex.column != -1:
				sys.stderr.write(" "*(ex.column - 1) + "^\n")
		raise Exception
	return term


def _compile(buf, simplify=True, verbose=False, debug=False):
	term = _parse(buf)
	if False:
		# FIXME: re-enable the simplifier
		import transf.parse.simplifier
		old = term
		term = transf.parse.simplifier.simplify(term)
	compiler = Compiler(debug=debug)
	code = compiler.definitions(term)
	if verbose:
		sys.stderr.write("input code:\n%s\n" % buf)
		sys.stderr.write("output code:\n%s\n" % code)
	return code


def _print_code(code):
	sys.stderr.write("input code:\n")
	lines = code.split("\n")
	lineno = 0
	for line in code.split("\n"):
		lineno += 1
		sys.stderr.write("%3d %s\n" % (lineno, line.expandtabs()))


def _exec(code, globals_, locals_):
	'''Execute the compiled code in the caller's namespace.'''
	from transf.parse import _builtins
	globals_["__builtins__"] = _builtins
	try:
		exec code in globals_, locals_
	except NameError:
		sys.stderr.write("globals: %s\n" % globals_.keys())
		sys.stderr.write("locals: %s\n" % locals_.keys())
		_print_code(code)
		raise
	except:
		_print_code(code)
		raise


def Transfs(buf, simplify=True, verbose=False, debug=False):
	'''Parse transformation definitions from a string.'''
	code = _compile(buf, simplify=simplify, verbose=verbose, debug=debug)
	caller = sys._getframe(1)
	globals_ = caller.f_globals
	locals_ = caller.f_locals
	_exec(code, globals_, locals_)


def Transf(buf, simplify=True, verbose=False, debug=False):
	'''Parse a transformation from a string.'''
	code = _compile("_tmp = %s" % buf, simplify=simplify, verbose=verbose, debug=debug)
	caller = sys._getframe(1)
	globals_ = caller.f_globals
	locals_ = caller.f_locals.copy()
	_exec(code, globals_, locals_)
	return locals_["_tmp"]
