#!/usr/bin/env python


import os
import sys
import re
import subprocess
import shutil


verbose = True
dummy = False


def find_exe(name):
	# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52224
	paths = os.environ['PATH']
	if sys.platform == 'win32':
		ext = '.exe'
	else:
		ext = ''
	for searchpath in paths.split(os.pathsep):
		path = os.path.join(searchpath, name + ext)
		if os.path.exists(path):
			return path
	return None


class Antlr:

	def __init__(self):
		self.find_antlr()

	def find_antlr(self):
		if find_exe('cantlr') is not None:
			self.command = ['cantlr']
		elif find_exe('runantlr') is not None:
			self.command = ['runantlr']
		else:
			self.command = ['java', '-cp', '/usr/share/java/antlr.jar', 'antlr.Tool']

	def run(self, grammar):
		args = [
			'-o', os.path.dirname(grammar),
			grammar
		]
		return subprocess.call(self.command + args)

antlr = Antlr()


class Grammar:

	def __init__(self, grammar):
		self.grammar = grammar

	def parse(self):
		arg = self.grammar
		argdir = os.path.dirname(self.grammar)

		self.depends = []
		self.targets = []
		self.depends.append(arg)
		for line in open(self.grammar, "rt"):
			mo = re.search(r"\bclass\s+(\w+)\s+extends\s+(\w+)\s*;", line)
			if mo:
				klass = mo.group(1)
				target = os.path.join(argdir, klass + ".py")
				self.targets.append(target)
			mo = re.search(r"\bimportVocab\s*=\s*(\w+)\s*;", line)
			if mo:
				depend = os.path.join(argdir, mo.group(1) + "TokenTypes.txt")
				#self.depends.append(depend)
			mo = re.search(r"\bexportVocab\s*=\s*(\w+)\s*;", line)
			if mo:
				target = os.path.join(argdir, mo.group(1) + "TokenTypes.txt")
				if target not in targets:
					self.targets.append(target)

	def uptodate(self):
		for target in self.targets:
			if not os.path.exists(target):
				return False
			for depend in self.depends:
				if os.path.getmtime(depend) > os.path.getmtime(target):
					return False
		return True

	def build(self):
		self.parse()
		if not self.uptodate():
			if verbose:
				print "Running antlr with %s" % self.grammar
			if not dummy:
				return not antlr.run(self.grammar)
		return True

	def clean(self):
		self.parse()
		for target in self.targets:
			if os.path.exists(target):
				if verbose:
					print "Removing %s" % target
				if not dummy:
					os.unlink(target)


def enumerate_grammars():
	for dirpath, dirnames, filenames in os.walk('.'):
		for filename in filenames:
			if filename.endswith('.g'):
				yield os.path.join(dirpath, filename)
		if '.hg' in dirnames:
			dirnames.remove('.hg')

targets = [Grammar(grammar) for grammar in enumerate_grammars()]


def build():
	success = True
	for target in targets:
		exit = target.build()
		success = success and exit
	if success:
		print "Build successful"
	else:
		print "Build not sucessful"


def clean():
	for target in targets:
		target.clean()


def test():
	import unittest
	testSuite = unittest.TestSuite()
	testLoader = unittest.defaultTestLoader
	if len(sys.argv) > 1:
		names = sys.argv[1:]
	else:
		names = [
			"aterm._tests",
			"aterm.asd",
			"transf._tests",
			"box._tests",
			"ir._tests",
			"refactoring._tests.RefactoringTestSuite",
		]
	for name in names:
		test = testLoader.loadTestsFromName(name)
		testSuite.addTest(test)
	testRunner = unittest.TextTestRunner(verbosity=2)
	result = testRunner.run(testSuite)
	sys.exit(not result.wasSuccessful())



def doc():
	modules = [
		'aterm',
		'transf',
		#'box',
		#'ir',
		#'ui',
	]
	shutil.rmtree("doc/html", ignore_errors=True)
	subprocess.call(
		['epydoc',
			'--no-private',
			'--no-sourcecode',
			'-o', 'doc/html'
		] + modules + sys.argv[1:]
	)


def dist():
	build()
	# TODO: write-me
	"""
	rm -f ../idc.tar.bz2
	tar -cjf ../idc.tar.bz2 \
		--exclude '.*.sw?' \
		--exclude '.svn' \
		--exclude '*.pyc' \
		--exclude 'doc' \
		.

	zip -r ../idc.zip . \
		-x '.*' \
		-x '*/.svn/*' \
		-x '*.pyc' \
		-x 'doc/*'
	"""


def py2exe():
	from distutils.core import setup
	import py2exe, glob

	sys.argv.append('py2exe')

	setup(
			windows = [{'script': "idc.py"}],
			options = {
				'py2exe': {
					'optimize': 2,
					'includes': 'cairo, pango, pangocairo, atk, gobject',
					#'excludes': 'antlraterm, antlr, antlrre, dasm, idc, setup, translate, aterm, box, dot, ir, machine, refactoring, transf, ui',
				}
			},
			data_files=[
				('examples', glob.glob('examples/*.s')),
			],
			#zipfile = "shared.lib",
	)


def pylint():
	"""Run pylint."""
	subprocess.call(['pylint', '--rcfile=pylintrc', 'aterm', 'transf'])


def main():
	try:
		command = sys.argv.pop(1)
	except IndexError:
		sys.stderr.write("usage:\n")
		sys.stderr.write("  %s build\n" % sys.argv[0])
		sys.stderr.write("  %s clean\n" % sys.argv[0])
		sys.stderr.write("  %s test\n" % sys.argv[0])
		sys.exit(1)
	try:
		func = globals()[command]
	except KeyError:
		sys.stderr.write("unknown command %r\n" % command)
		sys.exit(1)
	sys.exit(func())


if __name__ == '__main__':
	main()
