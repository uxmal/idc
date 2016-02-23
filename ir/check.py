'''Intermediate code correctness checking.
'''


import os.path

import aterm.asd

from transf import exception
from transf import transformation
from transf import lib
from transf import parse
from transf import util

import ir

asd = aterm.asd.parse(open(os.path.join(ir.__path__[0], 'ir.asdl'), 'rt').read())


class _Check(transformation.Transformation):

	def __init__(self, asd, production):
		transformation.Transformation.__init__(self)
		self.asd = asd
		self.production = production

	def apply(self, trm, ctx):
		try:
			self.asd.validate(self.production, trm)
		except aterm.asd.MismatchException, ex:
			raise exception.Fatal(str(ex))
		else:
			return trm

type = _Check(asd, "type")
expr = _Check(asd, "expr")
stmt = _Check(asd, "stmt")
module = _Check(asd, "module")


if __name__ == '__main__':
	import aterm.factory
	import sys

	factory = aterm.factory.factory

	for arg in sys.argv[1:]:
		term = factory.readFromTextFile(file(arg, 'rt'))
		sys.stderr.write('Checking %s ...\n' % arg)
		try:
			module(term)
		except exception.Failure:
			sys.stderr.write('FAILED\n')
		else:
			sys.stderr.write('OK\n')
		sys.stderr.write('\n')


