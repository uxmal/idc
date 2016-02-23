#!/usr/bin/env python
'''Unit tests.'''


import unittest

from aterm.factory import factory
from aterm import types
from aterm import lists
from aterm import annotation
from aterm import path


class TestTerm(unittest.TestCase):

	def parseArgs(self, args):
		return [factory.parse(value) for value in args]

	def parseKargs(self, kargs):
		res = {}
		for name, value in kargs.iteritems():
			res[name] = factory.parse(value)
		return res

	intTestCases = [
		'0',
		'1',
		'-2',
		'1234567890',
	]

	def failIfMutable(self, obj):
		# XXX: disabled
		return
		for name in dir(obj):
			try:
				setattr(obj, name, None)
			except AttributeError:
				pass
			else:
				self.fail('attribute "%s" is modifiable' % name)

			try:
				delattr(obj, name)
			except AttributeError:
				pass
			except TypeError:
				pass
			else:
				self.fail('attribute "%s" is deletable' % name)


	def testInt(self):
		for termStr in self.intTestCases:
			value = int(termStr)
			_term = factory.parse(termStr)
			self.failUnless(_term.factory is factory)
			self.failUnlessEqual(_term.getType(), types.INT)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)

	realTestCases = [
		'0.0',
		'1.2',
		'1.',
		'.1',
		'-1.2',
		'0.1E10',
		'0.1E-10',
		'0.1E+10',
		'1E10',
		'12345.67890',
	]

	def testReal(self):
		for termStr in self.realTestCases:
			value = float(termStr)
			_term = factory.parse(termStr)
			self.failUnless(_term.factory is factory)
			self.failUnlessEqual(_term.getType(), types.REAL)
			self.failUnlessAlmostEqual(_term.getValue(), value)
			self.failIfMutable(_term)

	strTestCases = [
		(r'""', ''),
		(r'" "', ' '),
		(r'"\""', "\""),
		(r'"\t"', '\t'),
		(r'"\r"', '\r'),
		(r'"\n"', '\n'),
	]

	def testStr(self):
		for termStr, value in self.strTestCases:
			_term = factory.parse(termStr)
			self.failUnless(_term.factory is factory)
			self.failUnlessEqual(_term.getType(), types.STR)
			self.failUnlessEqual(_term.getValue(), value)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)

	listTestCases = [
		('[]', 0),
		('[1]', 1),
		('[1,2]', 2),
		('[[],[1],[1,[2]]]', 3),
	]

	def testList(self):
		for termStr, length in self.listTestCases:
			_term = factory.parse(termStr)
			self.failUnless(_term.factory is factory)
			self.failUnless(_term.getType() & types.LIST)
			self.failUnlessEqual(not _term, length == 0)
			self.failUnlessEqual(len(_term), length)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)

	applTestCases = [
		('C', 'C', 0),
		('C(1)', 'C', 1),
		('C(1,2)', 'C', 2),
	]

	def testAppl(self):
		for termStr, name, arity in self.applTestCases:
			_term = factory.parse(termStr)
			self.failUnless(_term.factory is factory)
			self.failUnlessEqual(_term.type, types.APPL)
			self.failUnlessEqual(_term.name, name)
			self.failUnlessEqual(_term.getArity(), arity)
			self.failUnlessEqual(str(_term), termStr)
			self.failIfMutable(_term)

	identityTestCases = [
		# ints
		['1', '2'],

		# reals
		['0.1', '0.2'],

		# strings
		['""', '"s"', '"st"'],

		# lists
		['[]', '[1]', '[1,2]'],

		# applications
		['()', '(1)', '(1,2)'],
		['C', 'D', 'C(1)', 'C(1,2)'],
	]

	def testIdentity(self):
		annos = factory.parse('[1,2]')

		for terms1Str in self.identityTestCases:
			for terms2Str in self.identityTestCases:
				for term1Str in terms1Str:
					for term2Str in terms2Str:
						term1 = factory.parse(term1Str)
						term2 = factory.parse(term2Str)

						expectedResult = term1Str == term2Str

						result = term1.isEquivalent(term2)
						self.failUnlessEqual(result, expectedResult, msg = '%s <=> %s = %r (!= %r)' % (term1Str, term2Str, result, expectedResult))

						result = term1.isEqual(term2)
						self.failUnlessEqual(result, expectedResult, msg = '%s == %s = %r (!= %r)' % (term1Str, term2Str, result, expectedResult))

						if expectedResult and types.isAppl(term2):
							term2 = annotation.set(term2, factory.parse("A(1)"))

							result = term1.isEquivalent(term2)
							self.failUnlessEqual(result, True, msg = '%s <=> %s = %r (!= %r)' % (term1Str, term2Str, result, True))

							result = term1.isEqual(term2)
							self.failUnlessEqual(result, False, msg = '%s == %s = %r (!= %r)' % (term1Str, term2Str, result, False))


	def testWrite(self):
		for terms1Str in self.identityTestCases:
			for term1Str in terms1Str:
				term1 = factory.parse(term1Str)

				term2Str = str(term1)

				self.failUnlessEqual(term1Str, term2Str)

	matchTestCases = [
		# ints
		('1', '_', True, ['1'], {}),
		('1', 'x', True, [], {'x':'1'}),

		# reals
		('0.1', '_', True, ['0.1'], {}),
		('0.1', 'x', True, [], {'x':'0.1'}),

		# strings
		('"s"', '_', True, ['"s"'], {}),
		('"s"', 'x', True, [], {'x':'"s"'}),

		# lists
		('[]', '[*]', True, ['[]'], {}),
		('[]', '[*x]', True, [], {'x':'[]'}),
		('[1]', '[*]', True, ['[1]'], {}),
		('[1]', '[*x]', True, [], {'x':'[1]'}),
		('[1,2]', '[*]', True, ['[1,2]'], {}),
		('[1,2]', '[*x]', True, [], {'x':'[1,2]'}),
		('[1,2]', '[1,*]', True, ['[2]'], {}),
		('[1,2]', '[1,*x]', True, [], {'x':'[2]'}),
		('[1,2]', '[1,2,*]', True, ['[]'], {}),
		('[1,2]', '[1,2,*x]', True, [], {'x':'[]'}),
		('[1,2]', 'x', True, [], {'x':'[1,2]'}),
		('[1,0.2,"s"]', '[_,_,_]', True, ['1', '0.2', '"s"'], {}),
		('[1,0.2,"s"]', '[x,y,z]', True, [], {'x':'1', 'y':'0.2', 'z':'"s"'}),
		('[1,2,3]', '[_,*]', True, ['1', '[2,3]'], {}),
		('[1,2,3]', '[x,*y]', True, [], {'x':'1', 'y':'[2,3]'}),
		('[1,2,1,2]', '[x,y,x,y]', True, [], {'x':'1', 'y':'2'}),

		# appls
		('C', '_', True, ['C()'], {}),
		('C', 'x', True, [], {'x':'C()'}),
		('C()', '_', True, ['C'], {}),
		('C()', 'x', True, [], {'x':'C'}),
		('C(1)', '_', True, ['C(1)'], {}),
		('C(1)', 'x', True, [], {'x':'C(1)'}),
		('C(1,2)', '_', True, ['C(1,2)'], {}),
		('C(1,2)', 'x', True, [], {'x':'C(1,2)'}),
		('C(1)', 'C(_)', True, ['1'], {}),
		('C(1)', 'C(x)', True, [], {'x':'1'}),
		('C(1,2)', 'C(_,_)', True, ['1', '2'], {}),
		('C(1,2)', 'C(x,y)', True, [], {'x':'1', 'y':'2'}),
		('C(1,2,3)', '_(_,*)', True, ['"C"', '1', '[2,3]'], {}),
		('C(1,2,3)', 'f(x,*y)', True, [], {'f':'"C"', 'x':'1', 'y':'[2,3]'}),
		('C(1,2,3)', '_()', False, ['"C"'], {}),
		('C(1,2,3)', 'f()', False, [], {'f':'"C"'}),

		# tuples
		('(1,2,3)', '_(_,*)', True, ['""', '1', '[2,3]'], {}),
		('(1,2,3)', 'f(x,*y)', True, [], {'f':'""', 'x':'1', 'y':'[2,3]'}),
	]

	def testMatch(self):
		for termStr, patternStr, expectedResult, expectedArgsStr, expectedKargsStr in self.matchTestCases:

			term = factory.parse(termStr)
			expectedArgs = self.parseArgs(expectedArgsStr)
			expectedKargs = self.parseKargs(expectedKargsStr)

			match = factory.match(patternStr, term)
			result = bool(match)

			self.failUnlessEqual(result, expectedResult, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, result, expectedResult))
			if match:
				self.failUnlessEqual(match.args, expectedArgs, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, match.args, expectedArgs))
				self.failUnlessEqual(match.kargs, expectedKargs, msg = '%s ~ %s = %r (!= %r)' % (patternStr, termStr, match.kargs, expectedKargs))

	makeTestCases = [
		# constants terms
		('1', [], {}, '1'),
		('0.1', [], {}, '0.1'),
		('"s"', [], {}, '"s"'),
		('C', [], {}, 'C'),
		('[1,2]', [], {}, '[1,2]'),
		('C(1,2)', [], {}, 'C(1,2)'),

		# simple wildcard substitution
		('_', ['1'], {}, '1'),
		('_', ['0.1'], {}, '0.1'),
		('_', ['"s"'], {}, '"s"'),
		('_', ['C'], {}, 'C'),
		('_', ['[1,2]'], {}, '[1,2]'),
		('_', ['C(1,2)'], {}, 'C(1,2)'),

		# simple variable substitution
		('x', [], {'x':'1'}, '1'),
		('x', [], {'x':'0.1'}, '0.1'),
		('x', [], {'x':'"s"'}, '"s"'),
		('x', [], {'x':'C'}, 'C'),
		('x', [], {'x':'[1,2]'}, '[1,2]'),
		('x', [], {'x':'C(1,2)'}, 'C(1,2)'),

		# wildcard substitution in lists
		('[_]', ['1'], {}, '[1]'),
		('[_,_]', ['1', '2'], {}, '[1,2]'),
		('[*]', ['[1,2]'], {}, '[1,2]'),
		('[_,*]', ['1', '[2]'], {}, '[1,2]'),

		# variable substitution in lists
		('[x]', [], {'x':'1'}, '[1]'),
		('[x,y]', [], {'x':'1', 'y':'2'}, '[1,2]'),
		('[*x]', [], {'x':'[1,2]'}, '[1,2]'),
		('[x,*y]', [], {'x':'1', 'y':'[2]'}, '[1,2]'),

		# wildcard substitution in applications
		('C(_)', ['1'], {}, 'C(1)'),
		('C(_,_)', ['1', '2'], {}, 'C(1,2)'),
		('_()', ['"C"'], {}, 'C()'),
		('_(_,_)', ['"C"', '1', '2'], {}, 'C(1,2)'),
		('_(_,*)', ['"C"', '1', '[2]'], {}, 'C(1,2)'),

		# variable substitution in applications
		('C(x)', [], {'x':'1'}, 'C(1)'),
		('C(x,y)', [], {'x':'1', 'y':'2'}, 'C(1,2)'),
		('f()', [], {'f':'"C"'}, 'C()'),
		('f(x,y)', [], {'f':'"C"', 'x':'1', 'y':'2'}, 'C(1,2)'),
		('f(x,*y)', [], {'f':'"C"', 'x':'1', 'y':'[2]'}, 'C(1,2)'),
	]

	def testMake(self):
		for patternStr, argsStr, kargsStr, expectedResultStr in self.makeTestCases:
			args = self.parseArgs(argsStr)
			kargs = self.parseKargs(kargsStr)
			expectedResult = factory.parse(expectedResultStr)
			result = factory.make(patternStr, *args, **kargs)
			self.failUnlessEqual(result, expectedResult)

	def _testHash(self, cmpf, hashf, msg = None):
		for terms1Str in self.identityTestCases:
			for term1Str in terms1Str:
				term1 = factory.parse(term1Str)
				hash1 = hashf(term1)
				self.failUnless(isinstance(hash1, int))
				self.failIfEqual(hash1, -1)
				for terms2Str in self.identityTestCases:
					for term2Str in terms2Str:
						term2 = factory.parse(term2Str)
						hash2 = hashf(term2)
						term_eq = cmpf(term1, term2)
						hash_eq = hash1 == hash2
						detail = '%s (%d) and %s (%d)' % (
							term1Str, hash1, term2Str, hash2
						)
						if term_eq:
							self.failUnless(hash_eq,
								'%s hash/equality incoerence for '
								'%s' % (msg, detail)
							)
						elif 0:
							# XXX: this fails on python 2.3 but no on 2.4...
							self.failIf(hash_eq,
								'%s hash colision for '
								'%s' % (msg, detail)
							)

	def testHash(self):
		self._testHash(
			lambda t, o: t.isEquivalent(o),
			lambda t: t.getStructuralHash(),
			msg = 'structural'
		)
		self._testHash(
			lambda t, o: t.isEqual(o),
			lambda t: t.getHash(),
			msg = 'full'
		)
		self._testHash(
			lambda t, o: t == o,
			lambda t: hash(t),
			msg = 'python'
		)

	def testAnnotations(self):
		for terms1Str in self.identityTestCases:
			for term1Str in terms1Str:
				term1 = factory.parse(term1Str)
				if not types.isAppl(term1):
					continue

				term = term1
				self.failUnlessEqual(term.annotations, factory.parse("[]"))

				term = annotation.set(term, factory.parse("A(1)"))
				self.failUnlessEqual(term.annotations, factory.parse("[A(1)]"))

				term = annotation.set(term, factory.parse("B(2)"))
				self.failUnlessEqual(annotation.get(term, "A"), factory.parse("A(1)"))
				self.failUnlessEqual(annotation.get(term, "B"), factory.parse("B(2)"))

				term = annotation.set(term, factory.parse("A(3)"))
				self.failUnlessEqual(annotation.get(term, "A"), factory.parse("A(3)"))
				self.failUnlessEqual(annotation.get(term, "B"), factory.parse("B(2)"))

				term = annotation.remove(term, "A")
				self.failUnlessEqual(term.annotations, factory.parse("[B(2)]"))

				try:
					annotation.get(term, "C(_)")
					self.fail()
				except ValueError:
					pass

				self.failUnless(term.isEquivalent(term1))


class TestList(unittest.TestCase):

	splitTestCases = [
		('[0,1,2,3]', 0, '[]', '[0,1,2,3]'),
		('[0,1,2,3]', 1, '[0,]', '[1,2,3]'),
		('[0,1,2,3]', 2, '[0,1,]', '[2,3]'),
		('[0,1,2,3]', 3, '[0,1,2,]', '[3]'),
		('[0,1,2,3]', 4, '[0,1,2,3]', '[]'),
	]

	def testSplit(self):
		for inputStr, index, expectedHeadStr, expectedTailStr in self.splitTestCases:
			input = factory.parse(inputStr)
			expectedHead = factory.parse(expectedHeadStr)
			expectedTail = factory.parse(expectedTailStr)

			head, tail = lists.split(input, index)

			self.failUnlessEqual(head, expectedHead)
			self.failUnlessEqual(tail, expectedTail)

	rangeTestCases = [
		('[0,1,2]', 0, 0, '[0,1,2]'),
		('[0,1,2]', 0, 1, '[X(0),1,2]'),
		('[0,1,2]', 0, 2, '[X(0),X(1),2]'),
		('[0,1,2]', 0, 3, '[X(0),X(1),X(2)]'),
		('[0,1,2]', 1, 1, '[0,1,2]'),
		('[0,1,2]', 1, 2, '[0,X(1),2]'),
		('[0,1,2]', 1, 3, '[0,X(1),X(2)]'),
		('[0,1,2]', 2, 2, '[0,1,2]'),
		('[0,1,2]', 2, 3, '[0,1,X(2)]'),
		('[0,1,2]', 3, 3, '[0,1,2]'),
	]



class TestPath(unittest.TestCase):

	testCompareTestCases = [
		([1,2], [], path.ANCESTOR),
		([1,2], [0], path.PRECEDENT),
		([1,2], [1], path.ANCESTOR),
		([1,2], [1,1], path.PRECEDENT),
		([1,2], [1,2], path.EQUAL),
		([1,2], [1,2,0], path.DESCENDENT),
		([1,2], [1,3], path.SUBSEQUENT),
		([1,2], [2], path.SUBSEQUENT),
	]

	def testCompare(self):
		for path1, path2, expectedResult in self.testCompareTestCases:
			path1 = path.Path(path1)
			path2 = path.Path(path2)
			result = path1.compare(path2)
			self.failUnlessEqual(result, expectedResult, '%s vs %s == %s (!= %s)' % (path1, path2, result, expectedResult))

	testAncestorTestCases = [
		([1,2], [], []),
		([1,2], [0], []),
		([1,2], [1], [1]),
		([1,2], [1,1], [1]),
		([1,2], [1,2], [1,2]),
		([1,2], [1,2,0], [1,2]),
		([1,2], [1,3], [1]),
		([1,2], [2], []),
	]

	def testAncestor(self):
		for path1, path2, expectedResult in self.testAncestorTestCases:
			path1 = path.Path(path1)
			path2 = path.Path(path2)
			expectedResult = path.Path(expectedResult)
			result = path1.ancestor(path2)
			self.failUnlessEqual(result, expectedResult, '%s vs %s == %s (!= %s)' % (path1, path2, result, expectedResult))

	projectTestCases = [
		('1', '/', '1'),
		('[1,2]', '/', '[1,2]'),
		('[1,2]', '/0/', '1'),
		('[1,2]', '/1/', '2'),
		('C(1,2)', '/', 'C(1,2)'),
		('C(1,2)', '/0/', '1'),
		('C(1,2)', '/1/', '2'),
		('A([B,C],[D,E])', '/0/0/', 'B'),
		('A([B,C],[D,E])', '/0/1/', 'C'),
		('A([B,C],[D,E])', '/1/0/', 'D'),
		('A([B,C],[D,E])', '/1/1/', 'E'),
	]

	def testProject(self):
		for termStr, pathStr, expectedResultStr in self.projectTestCases:
			term = factory.parse(termStr)
			path_ = path.Path.fromStr(pathStr)
			expectedResult = factory.parse(expectedResultStr)
			result = path_.project(term)
			self.failUnlessEqual(result, expectedResult, '%s . %s == %s (!= %s)' % (termStr, pathStr, result, expectedResult))

	transformTestCases = [
		('1', '/', 'X(1)'),
		('[1,2]', '/', 'X([1,2])'),
		('[1,2]', '/0/', '[X(1),2]'),
		('[1,2]', '/1/', '[1,X(2)]'),
		('C(1,2)', '/', 'X(C(1,2))'),
		('C(1,2)', '/0/', 'C(X(1),2)'),
		('C(1,2)', '/1/', 'C(1,X(2))'),
		('A([B,C],[D,E])', '/0/1/', 'A([B,X(C)],[D,E])'),
		('A([B,C],[D,E])', '/1/0/', 'A([B,C],[X(D),E])'),
	]

	def testTransform(self):
		func = lambda x: x.factory.make('X(_)', x)
		for termStr, pathStr, expectedResultStr in self.transformTestCases:
			term = factory.parse(termStr)
			path_ = path.Path.fromStr(pathStr)
			expectedResult = factory.parse(expectedResultStr)
			result = path_.transform(term, func)
			self.failUnlessEqual(result, expectedResult, '%s . %s == %s (!= %s)' % (termStr, pathStr, result, expectedResult))

	annotateTestCases = [
		('A', 'A{Path([])}'),
		('[A,B]', '[A{Path([0])},B{Path([1])}]'),
		('C(A,B)', 'C(A{Path([0])},B{Path([1])}){Path([])}'),
		('[[C]]', '[[C{Path([0,0])}]]'),
		('C(C(C))', 'C(C(C{Path([0,0])}){Path([0])}){Path([])}'),
		('[[A],[B]]', '[[A{Path([0,0])}],[B{Path([0,1])}]]'),
		('C(C(A),C(B))', 'C(C(A{Path([0,0])}){Path([0])},C(B{Path([0,1])}){Path([1])}){Path([])}'),
	]

	def testAnnotate(self):
		for termStr, expectedResultStr in self.annotateTestCases:
			term = factory.parse(termStr)
			expectedResult = factory.parse(expectedResultStr)
			result = path.annotate(term)
			self.failUnlessEqual(result, expectedResult)

	def testDeAnnotate(self):
		for expectedResultStr, termStr in self.annotateTestCases:
			term = factory.parse(termStr)
			expectedResult = factory.parse(expectedResultStr)
			result = path.deannotate(term)
			self.failUnlessEqual(result, expectedResult)


if __name__ == '__main__':
	unittest.main()
