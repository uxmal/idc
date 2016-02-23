#!/usr/bin/env python


import unittest

import aterm.factory
import box

import transf._tests


class TestWriter(unittest.TestCase):
	
	def setUp(self):
		self.factory = aterm.factory.factory

	def parseArgs(self, args):
		return [self.factory.parse(value) for value in args]
	
	def parseKargs(self, kargs):
		res = {}
		for name, value in kargs.iteritems():
			res[name] = self.factory.parse(value)
		return res
	
	box2TextTestCases = [
		('"a"', 'a'),
		('H(["a","b"])', 'ab'),
		('V(["a","b"])', 'a\nb\n'),
		('V(["a",I("b"),"c"])', 'a\n\tb\nc\n'),
	]
	
	def testBox2Text(self):
		for inputStr, expectedOutput in self.box2TextTestCases:
			input = self.factory.parse(inputStr)
		
			output = box.stringify(input)
			
			self.failUnlessEqual(output, expectedOutput)

	term2BoxTestCases = [
	]
	
	def _testTerm2Box(self):
		for inputStr, expectedOutput in self.term2BoxTestCases:
			input = self.factory.parse(inputStr)
		
			boxes = box.term2box(input)
			output = box.stringify(boxes)
			
			self.failUnlessEqual(output, expectedOutput)


class TestTransfs(transf._tests.TestMixin, unittest.TestCase):
	
	commasTestCases = [
		('[ "A", "B", "C" ]', 'H([ "A", ", ", "B", ", ", "C" ])'),
	]
	
	def testCommas(self):
		self._testTransf(box.commas, self.commasTestCases)


if __name__ == '__main__':
	unittest.main()
