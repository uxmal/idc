#!/usr/bin/env python


import unittest

import aterm.factory
import box

import transf.exception

import ir.check
import ir.pprint


class TestPrettyPrint(unittest.TestCase):

	def setUp(self):
		self.factory = aterm.factory.factory

	def parseArgs(self, args):
		return [self.factory.parse(value) for value in args]

	def parseKargs(self, kargs):
		res = {}
		for name, value in kargs.iteritems():
			res[name] = self.factory.parse(value)
		return res

	checkerTestCases = {
		'expr': [
			('Binary(Plus(Int(32,Signed)),Lit(Int(32,Unsigned),1),Sym("x"))', True),
		],

		'stmt': [
			('Label("label")', True),
			('Asm("ret",[])', True),
			('Asm("mov",[Sym("ax"), Lit(Int(32,Signed),1000)])', True),
			('Function(Void,"main",[],[])', True),
		],

		'module': [
			("Module([])", True),
			("XXX", False),
		],
	}

	def testChecker(self):
		checker = ir.check
		for methodName, subTestCases in self.checkerTestCases.iteritems():
			for inputStr, expectedOutput in subTestCases:
				input = self.factory.parse(inputStr)

				try:
					getattr(checker, methodName)(input)
					output = True
				except transf.exception.Fatal, ex:
					output = False

				self.failUnlessEqual(
						output, expectedOutput,
						msg = '%s(%s) = %r (%r expected)' % (methodName, inputStr, output, expectedOutput)
				)

	prettyPrinterTestCases = {
		'ppExpr': [
			('Binary(Plus(Int(32,Signed)),Lit(Int(32,Unsigned),1),Sym("x"))', '1 + x'),
		],

		'ppStmt': [
			('Label("label")', 'label:'),
			('Asm("ret",[])', 'asm("ret");'),
			('Asm("mov",[Sym("ax"), Lit(Int(32,Signed),1000)])', 'asm("mov", ax, 1000);'),
			('Function(Void,"main",[],[])', 'void main()\n{\n}\n'),
		],
	}

	def testPrettyPrinter(self):
		for methodName, subTestCases in self.prettyPrinterTestCases.iteritems():
			for inputStr, expectedOutput in subTestCases:
				input = self.factory.parse(inputStr)
				boxes = getattr(ir.pprint, methodName)(input)
				output = box.stringify(boxes)
				self.failUnlessEqual(output, expectedOutput)


if __name__ == '__main__':
	unittest.main()
