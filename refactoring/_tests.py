#!/usr/bin/env python


import os
import unittest
import traceback

import aterm.factory
import transf.transformation
import refactoring


class TransformationTest(unittest.TestCase):
	'''A test case based on a transformation.'''

	def __init__(self, transf, transfName = None):
		unittest.TestCase.__init__(self)
		self.__transf = transf
		self.__transfName = transfName

	def runTest(self):
		try:
			self.__transf(aterm.factory.factory.makeStr("Ignored"))
		except transf.exception.Failure, ex:
			traceback.print_exc()
			self.fail(msg = str(ex))

	def shortDescription(self):
		return self.__transfName


class RefactoringTestSuite(unittest.TestSuite):

	def __init__(self):
		unittest.TestSuite.__init__(self)

		for name in os.listdir(refactoring.__path__[0]):
			name, ext = os.path.splitext(name)
			if name not in ('__init__', '_tests') and ext == '.py':
				try:
					module = __import__('refactoring.' + name)
				except:
					traceback.print_exc()
				else:
					module = getattr(module, name)
					for nam in dir(module):
						obj = getattr(module, nam)
						if nam.startswith('test') and isinstance(obj, transf.transformation.Transformation):
							test = TransformationTest(obj, module.__name__ + '.' + nam)
							self.addTest(test)
						if isinstance(obj, unittest.TestCase):
							self.addTest(obj)

if __name__ == '__main__':
	unittest.main(defaultTest='RefactoringTestSuite')
