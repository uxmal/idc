#!/usr/bin/env python
'''Unit tests for the transformation package.'''


import unittest

import antlr

import aterm.factory

from transf import transformation
from transf import parse
from transf.lib import *
from transf.lib.base import ident, fail


Transf = parse.Transf
Rule = Transf


class TestMixin:

	termInputs = [
		'0',
		'1',
		'2',
		'0.0',
		'0.1',
		'0.2',
		'""',
		'"a"',
		'"b"',
		'[]',
		'[1]',
		'[1,2]',
		'C',
		'C(1)',
		'D',
	]

	def setUp(self):
		self.factory = aterm.factory.factory

	def _testTransf(self, transf, testCases):
		for termStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			expectedResult = self.factory.parse(expectedResultStr)

			try:
				result = transf(term)
			except exception.Failure:
				result = self.factory.parse('FAILURE')

			self.failUnless(isinstance(result, aterm.term.Term),
				msg = "not a term: %s -> %s (!= %s)" % (term, result, expectedResult)
			)

			self.failUnless(expectedResult.isEqual(result),
				msg = "%s -> %s (!= %s)" %(term, result, expectedResult)
			)

	def _testMetaTransf(self, metaTransf, testCases):
		result = []
		operands, rest = testCases
		for termStr, expectedResultStrs in rest.iteritems():
			for operand, expectedResultStr in zip(operands, expectedResultStrs):
				self._testTransf(metaTransf(operand), [(termStr, expectedResultStr)])


class TestCombine(TestMixin, unittest.TestCase):

	identTestCases = [(term, term) for term in TestMixin.termInputs]
	failTestCases = [(term, 'FAILURE') for term in TestMixin.termInputs]
	xxxTestCases = [(term, 'X') for term in TestMixin.termInputs]

	def testIdent(self):
		self._testTransf(ident, self.identTestCases)
		self._testTransf(Transf('id'), self.identTestCases)

	def testFail(self):
		self._testTransf(fail, self.failTestCases)
		self._testTransf(Transf('fail'), self.failTestCases)

	unaryTestCases = [
		[0], [1], [2],
	]

	binaryTestCases = [
		[0, 0], [0, 1], [0, 2],
		[1, 0], [1, 1], [1, 2],
		[2, 0], [2, 1], [2, 2],
	]

	ternaryTestCases = [
		[0, 0, 0], [0, 0, 1], [0, 0, 2],
		[0, 1, 0], [0, 1, 1], [0, 1, 2],
		[0, 2, 0], [0, 2, 1], [0, 2, 2],
		[1, 0, 0], [1, 0, 1], [1, 0, 2],
		[1, 1, 0], [1, 1, 1], [1, 1, 2],
		[1, 2, 0], [1, 2, 1], [1, 2, 2],
		[2, 0, 0], [2, 0, 1], [2, 0, 2],
		[2, 1, 0], [2, 1, 1], [2, 1, 2],
		[2, 2, 0], [2, 2, 1], [2, 2, 2],
	]

	def _testCombination(self, Transf, n, func):
		argTable = {
			0: fail,
			1: ident,
			2: Rule('_ -> X'),
		}
		testCaseTable = {
			1: self.unaryTestCases,
			2: self.binaryTestCases,
			3: self.ternaryTestCases,
		}
		resultTable = {
			0: self.failTestCases,
			1: self.identTestCases,
			2: self.xxxTestCases,
		}
		testCases = testCaseTable[n]
		for args in testCases:
			transf = Transf(*map(argTable.get, args))
			result = int(func(*args))
			resultCases = resultTable[result]
			try:
				self._testTransf(transf, resultCases)
			except AssertionError:
				self.fail(msg = "%s => ? != %s" % (args, result))

	def testNot(self):
		func = lambda x: not x
		self._testCombination(combine._Not, 1, func)
		self._testCombination(combine.Not, 1, func)

	def testTry(self):
		func = lambda x: x or 1
		self._testCombination(combine._Try, 1, func)
		self._testCombination(combine.Try, 1, func)

	def testChoice(self):
		func = lambda x, y: x or y
		self._testCombination(combine._Choice, 2, func)
		self._testCombination(combine.Choice, 2, func)
		self._testCombination(lambda x, y: Transf('x + y'), 2, func)

	def testComposition(self):
		func = lambda x, y: x and y and max(x, y) or 0
		self._testCombination(combine._Composition, 2, func)
		self._testCombination(combine.Composition, 2, func)
		self._testCombination(lambda x, y: Transf('x ; y'), 2, func)

	def testGuardedChoice(self):
		func = lambda x, y, z: (x and y and max(x, y) or 0) or (not x and z)
		self._testCombination(combine._GuardedChoice, 3, func)
		self._testCombination(combine.GuardedChoice, 3, func)
		self._testCombination(lambda x, y, z: Transf('x & y + z'), 3, func)

	def testIf(self):
		func = lambda x, y: (x and y) or (not x)
		self._testCombination(combine._If, 2, func)
		self._testCombination(combine.If, 2, func)
		self._testCombination(lambda x, y: Transf('if x then y end'), 2, func)

	def testIfElse(self):
		func = lambda x, y, z: (x and y) or (not x and z)
		self._testCombination(combine._IfElse, 3, func)
		self._testCombination(combine.IfElse, 3, func)
		self._testCombination(lambda x, y, z: Transf("if x then y else z end"), 3, func)


class TestMatch(TestMixin, unittest.TestCase):

	def _testMatchTransf(self, transf, *matchStrs):
		testCases = []
		for termStr in self.termInputs:
			if termStr in matchStrs:
				resultStr = termStr
			else:
				resultStr = 'FAILURE'
			testCases.append((termStr, resultStr))
		self._testTransf(transf, testCases)

	def testInt(self):
		self._testMatchTransf(match.Int(1), '1')
		self._testMatchTransf(Transf('?1'), '1')

	def testReal(self):
		self._testMatchTransf(match.Real(0.1), '0.1')
		self._testMatchTransf(Transf('?0.1'), '0.1')

	def testStr(self):
		self._testMatchTransf(match.Str("a"), '"a"')
		self._testMatchTransf(Transf('?"a"'), '"a"')

	def testNil(self):
		self._testMatchTransf(match.nil, '[]')
		self._testMatchTransf(Transf('?[]'), '[]')

	def testCons(self):
		self._testMatchTransf(match.Cons(match.Int(1),match.nil), '[1]')
		self._testMatchTransf(Transf('?[1]'), '[1]')

	def testList(self):
		self._testMatchTransf(match.List([match.Int(1),match.Int(2)]), '[1,2]')
		self._testMatchTransf(Transf('?[1,2]'), '[1,2]')

	def testAppl(self):
		self._testMatchTransf(match.Appl("C", ()), 'C')
		self._testMatchTransf(match.ApplCons(match.Str("C"), match.nil), 'C')
		self._testMatchTransf(Transf('?C()'), 'C')
		self._testMatchTransf(Transf('?C(1)'), 'C(1)')
		self._testMatchTransf(Transf('?C(1,2)'), 'C(1,2)')


class TestTraverse(TestMixin, unittest.TestCase):

	allTestCases = (
		[ident, fail, Rule('x -> X(x)')],
		{
			'A()': [
				'A()',
				'A()',
				'A()',
			],
			'A(B,C)': [
				'A(B,C))',
				'FAILURE',
				'A(X(B),X(C))',
			],
			'A(B(C,D),E(F,G))': [
				'A(B(C,D),E(F,G))',
				'FAILURE',
				'A(X(B(C,D)),X(E(F,G)))',
			],
		}
	)

	def testAll(self):
		self._testMetaTransf(traverse.All, self.allTestCases)

	oneTestCases = (
		[ident, fail, Rule('X -> Y')],
		{
			'1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'0.1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'"s"': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'X()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A(X)': ['A(X)', 'FAILURE', 'A(Y)'],
			'A(B,C)': ['A(B,C))', 'FAILURE', 'FAILURE'],
			'A(X,B)': ['A(X,B))', 'FAILURE', 'A(Y,B)'],
			'A(B,X)': ['A(B,X))', 'FAILURE', 'A(B,Y)'],
			'A(X,X)': ['A(X,X))', 'FAILURE', 'A(Y,X)'],
		}
	)

	def testOne(self):
		self._testMetaTransf(traverse.One, self.oneTestCases)

	someTestCases = (
		[ident, fail, Rule('X -> Y')],
		{
			'1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'0.1': ['FAILURE', 'FAILURE', 'FAILURE'],
			'"s"': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'X()': ['FAILURE', 'FAILURE', 'FAILURE'],
			'A(X)': ['A(X)', 'FAILURE', 'A(Y)'],
			'A(B,C)': ['A(B,C))', 'FAILURE', 'FAILURE'],
			'A(X,B)': ['A(X,B))', 'FAILURE', 'A(Y,B)'],
			'A(B,X)': ['A(B,X))', 'FAILURE', 'A(B,Y)'],
			'A(X,X)': ['A(X,X))', 'FAILURE', 'A(Y,Y)'],
		}
	)

	def testSome(self):
		self._testMetaTransf(traverse.Some, self.someTestCases)

	bottomUpTestCases = (
		[ident, fail, Rule('x -> X(x)')],
		{
			'A()': [
				'A()',
				'FAILURE',
				'X(A())',
			],
			'A(B(C,D),E(F,G))': [
				'A(B(C,D),E(F,G))',
				'FAILURE',
				'X(A(X(B(X(C),X(D))),X(E(X(F),X(G)))))',
			],
		}
	)

	def testBottomUp(self):
		self._testMetaTransf(traverse.BottomUp, self.bottomUpTestCases)

	topDownTestCases = (
		[ident, fail, combine.Try(Rule('f(x,y) -> X(x,y)'))],
		{
			'A()': [
				'A()',
				'FAILURE',
				'A()',
			],
			'A(B(C,D),E(F,G))': [
				'A(B(C,D),E(F,G))',
				'FAILURE',
				'X(X(C,D),X(F,G))',
			],
		}
	)

	def testTopdown(self):
		self._testMetaTransf(traverse.TopDown, self.topDownTestCases)

	# TODO: testInnerMost


class TestProject(TestMixin, unittest.TestCase):

	subtermsTestCases = (
		('1', '[]'),
		('0.1', '[]'),
		('"a"', '[]'),
		('[]', '[]'),
		('[1]', '[1]'),
		('[1,2]', '[1,2]'),
		('C', '[]'),
		('C(1)', '[1]'),
		('C(1,2)', '[1,2]'),
	)

	def testSubterms(self):
		self._testTransf(project.subterms, self.subtermsTestCases)


class TestUnify(TestMixin, unittest.TestCase):

	foldrTestCases = (
		('[1,2,3]', '6'),
	)

	def testFoldr(self):
		self._testTransf(
			unify.Foldr(build.Int(0), arith.Add),
			self.foldrTestCases
		)

	crushTestCases = (
		('[1,2]', '[1,[2,[]]]'),
		('C(1,2)', '[1,[2,[]]]'),
	)

	def testCrush(self):
		self._testTransf(
			unify.Crush(ident, lambda x,y: build.List([x, y]), ident),
			self.crushTestCases
		)

	collectAllTestCases = (
		('1', '[1]'),
		('[1,2]', '[1,2]'),
		('C(1,2)', '[1,2]'),
		('[[1,2],C(3,4)]', '[1,2,3,4]'),
		('C([1,2],C(3,4))', '[1,2,3,4]'),
	)

	def testCollectAll(self):
		self._testTransf(
			unify.CollectAll(match.anInt),
			self.collectAllTestCases
		)


class TestAnno(TestMixin, unittest.TestCase):

	def _testAnnoTransf(self, Transf, testCases):
		for input, label, output in testCases:
			trf = Transf(parse.Transf(label))
			self._testTransf(trf, [(input, output)])

	setTestCases = (
		('X', '!A(1)', 'X{A(1)}'),
		('X{B(2)}', '!A(1)', 'X{A(1),B(2)}'),
		('X{A(1)}', '!A(2)', 'X{A(2)}'),
		('X{A(1),B(2)}', '!A(2)', 'X{A(2),B(2)}'),
		('X{B(1),A(2)}', '!A(1)', 'X{A(1),B(1)}'),
		('1', '!A', '1'),
	)

	def testSet(self):
		self._testAnnoTransf(annotation.Set, self.setTestCases)

	getTestCases = (
		('X{A(1)}', '?A', 'A(1)'),
		('X{A(1),B(2)}', '?A', 'A(1)'),
		('X{B(1),A(2)}', '?A', 'A(2)'),
		('X{B(1)}', '?A', 'FAILURE'),
		('X', '?A', 'FAILURE'),
		('1', '?A', 'FAILURE'),
	)

	def testGet(self):
		self._testAnnoTransf(annotation.Get, self.getTestCases)

	hasTestCases = (
		('X{A(1)}', '?A', 'X{A(1)}'),
		('X{A(1),B(2)}', '?A', 'X{A(1),B(2)}'),
		('X{B(1),A(2)}', '?A', 'X{B(1),A(2)}'),
		('X{B(1)}', '?A', 'FAILURE'),
		('X', '?A', 'FAILURE'),
		('1', '?A', 'FAILURE'),
	)

	def testGet(self):
		self._testAnnoTransf(annotation.Has, self.hasTestCases)

	delTestCases = (
		('X', '?A', 'X'),
		('X{B(2)}', '?A', 'X{B(2)}'),
		('X{A(1)}', '?A', 'X'),
		('X{A(1),B(2)}', '?A', 'X{B(2)}'),
		('X{B(1),A(2)}', '?A', 'X{B(1)}'),
		('1', '?A', '1'),
	)

	def testDel(self):
		self._testAnnoTransf(annotation.Del, self.delTestCases)


class TestArith(TestMixin, unittest.TestCase):

	addTestCases = (
		('[1,2]', '3'),
	)

	def testAdd(self):
		self._testTransf(
			arith.Add(project.first, project.second),
			self.addTestCases
		)


class TestParse(TestMixin, unittest.TestCase):

	parseTestCases = [
		# base
		('id', 'Ident'),
		('fail', 'Fail'),

		# match
		('?1', 'Match(Int(1))'),
		('?0.1', 'Match(Real(0.1))'),
		('?"s"', 'Match(Str("s"))'),
		('?[]', 'Match(Nil)'),
		('?[1,2]', 'Match(Cons(Int(1),Cons(Int(2),Nil)))'),
		('?[1,*[2]]', 'Match(Cons(Int(1),Cons(Int(2),Nil)))'),
		('?C', 'Match(ApplName("C"))'),
		('?C(1,2)', 'Match(Appl("C",[Int(1),Int(2)]))'),
		('?_', 'Match(Wildcard)'),
		('?_(_,_)', 'Match(ApplCons(Wildcard,Cons(Wildcard,Cons(Wildcard,Nil))))'),
		('?x', 'Match(Var("x"))'),
		('?f(x,y)', 'Match(ApplCons(Var("f"),Cons(Var("x"),Cons(Var("y"),Nil))))'),
		('?C{X,Y,Z}', 'Match(Annos(ApplName("C"),Cons(ApplName("X"),Cons(ApplName("Y"),Cons(ApplName("Z"),Nil)))))'),

		# build
		('!1', 'Build(Int(1))'),
		('!0.1', 'Build(Real(0.1))'),
		('!"s"', 'Build(Str("s"))'),
		('![]', 'Build(Nil)'),
		('![1,2]', 'Build(Cons(Int(1),Cons(Int(2),Nil)))'),
		('![1,*[2]]', 'Build(Cons(Int(1),Cons(Int(2),Nil)))'),
		('![*[1],*[2]]', 'Build(Cat(Cons(Int(1),Nil),Cons(Int(2),Nil)))'),
		('!C', 'Build(ApplName("C"))'),
		('!C(1,2)', 'Build(Appl("C",[Int(1),Int(2)]))'),
		('!_', 'Build(Wildcard)'),
		('!_(_,_)', 'Build(ApplCons(Wildcard,Cons(Wildcard,Cons(Wildcard,Nil))))'),
		('!x', 'Build(Var("x"))'),
		('!f(x,y)', 'Build(ApplCons(Var("f"),Cons(Var("x"),Cons(Var("y"),Nil))))'),
		('!C{X,Y,Z}', 'Build(Annos(ApplName("C"),Cons(ApplName("X"),Cons(ApplName("Y"),Cons(ApplName("Z"),Nil)))))'),

		# congruent
		('~C(1, <id>)', 'Congruent(Appl("C",[Int(1),Wrap(Ident)]))'),

		# combine
		('id ; fail', 'Composition(Ident,Fail)'),
		('id + fail', 'LeftChoice(Ident,Fail)'),
		('id + fail ; id', 'LeftChoice(Ident,Composition(Fail,Ident))'),
		('(id + fail) ; id', 'Composition(LeftChoice(Ident,Fail),Ident)'),
		('?1 & !2 + !3', 'GuardedChoice(Match(Int(1)),Build(Int(2)),Build(Int(3)))'),
		('?1 & !2 + !3 + !4', 'GuardedChoice(Match(Int(1)),Build(Int(2)),LeftChoice(Build(Int(3)),Build(Int(4))))'),
		('?1 + !2 + !3 + !4', 'LeftChoice(Match(Int(1)),LeftChoice(Build(Int(2)),LeftChoice(Build(Int(3)),Build(Int(4)))))'),
		('if ?c then !x end', 'If([IfClause(Match(Var("c")),Build(Var("x")))],Ident)'),
		('if ?c then !x else !y end', 'If([IfClause(Match(Var("c")),Build(Var("x")))],Build(Var("y")))'),
		('switch !x case 1: !A case 2,3: !B else !C end', 'Switch(Build(Var("x")),[SwitchCase([Int(1)],Build(ApplName("A"))),SwitchCase([Int(2),Int(3)],Build(ApplName("B")))],Build(ApplName("C")))'),

		# wrap
		('?C(<id>,<fail>)', 'Match(Appl("C",[Wrap(Ident),Wrap(Fail)]))'),
		('!C(<id>,<fail>)', 'Build(Appl("C",[Wrap(Ident),Wrap(Fail)]))'),
		('?C(<v := id>,<fail>)', 'Match(Appl("C",[Wrap(ApplyAssign(Var("v"),Ident)),Wrap(Fail)]))'),

		# reference
		('base.ident', 'Transf("base.ident")'),
		('base.Ident()', 'Macro("base.Ident",[])'),

		# rules
		('C(x,y) -> D(y,x)', 'Rule(Appl("C",[Var("x"),Var("y")]),Appl("D",[Var("y"),Var("x")]))'),
		('C(x,y) -> D(y,x)', 'Rule(Appl("C",[Var("x"),Var("y")]),Appl("D",[Var("y"),Var("x")]))'),
		('1 -> 2 if a', 'RuleIf(Int(1),Int(2),Transf("a"))'),
		('1 -> 2 if a ; b | c', 'Choice([Composition(RuleIf(Int(1),Int(2),Transf("a")), Transf("b")),Transf("c")])'),
		('1 -> 2 if a + b | c', 'Choice([LeftChoice(RuleIf(Int(1),Int(2),Transf("a")), Transf("b")),Transf("c")])'),

		# scoping
		('with a, b in id end', 'Scope(["a","b"],Ident)'),
		('{a, b: id}', 'Scope(["a","b"],Ident)'),

		# application
		('id 123', 'BuildApply(Ident,Int(123))'),
		('id[1,2]', 'BuildApply(Ident,Cons(Int(1),Cons(Int(2),Nil)))'),

		# assignment
		('id => a', 'ApplyMatch(Ident,Var("a"))'),
		('a := !1', 'ApplyAssign(Var("a"),Build(Int(1)))'),
		('[a,b] := ![1,2]', 'ApplyAssign(Cons(Var("a"),Cons(Var("b"),Nil)),Build(Cons(Int(1),Cons(Int(2),Nil))))'),
		('a := id 123', 'ApplyAssign(Var("a"),BuildApply(Ident,Int(123)))'),

		# join operators
		('!1 / a \\ !2', 'Join(Build(Int(1)),Build(Int(2)),["a"],[])'),
		('!1 / a \\ \\ b / !2', 'Join(Build(Int(1)),Build(Int(2)),["a"],["b"])'),
		('/ a \\* !2', 'Iterate(Build(Int(2)),["a"],[])'),
		('/ a \\ \\ b /* !2', 'Iterate(Build(Int(2)),["a"],["b"])'),
	]

	def testParse(self):
		if False:
			print
			for input, expectedResult in self.parseTestCases:
				result = parse._parse(input, production="transf")
				print "\t\t(%r, %r)," % (input, str(result))
			print
		for input, expectedResult in self.parseTestCases:
			expectedResult = self.factory.parse(expectedResult)
			try:
				result = parse._parse(input, production="transf")
			except:
				print input
				raise
			self.failUnless(expectedResult.isEqual(result),
				msg = "%r -> %s (!= %s)" %(input, result, expectedResult)
			)


class TestPath(TestMixin, unittest.TestCase):

	def testAnnotate(self):
		self._testTransf(
			path.annotate,
			(
				('A', 'A{Path([])}'),
				('[A,B]', '[A{Path([0])},B{Path([1])}]'),
				('C(A,B)', 'C(A{Path([0])},B{Path([1])}){Path([])}'),
				('[[C]]', '[[C{Path([0,0])}]]'),
				('C(C(C))', 'C(C(C{Path([0,0])}){Path([0])}){Path([])}'),
				('[[A],[B]]', '[[A{Path([0,0])}],[B{Path([0,1])}]]'),
				('C(C(A),C(B))', 'C(C(A{Path([0,0])}){Path([0])},C(B{Path([0,1])}){Path([1])}){Path([])}'),
			)
		)

	def checkTransformation(self, metaTransf, testCases):
		for termStr, pathStr, expectedResultStr in testCases:
			term = self.factory.parse(termStr)
			_path = self.factory.parse(pathStr)
			expectedResult = self.factory.parse(expectedResultStr)

			result = metaTransf(_path)(term)

			self.failUnlessEqual(result, expectedResult)

	projectTestCases = [
		('1', '[]', '1'),
		('[1,2]', '[]', '[1,2]'),
		('[1,2]', '[0]', '1'),
		('[1,2]', '[1]', '2'),
		('C(1,2)', '[]', 'C(1,2)'),
		('C(1,2)', '[0]', '1'),
		('C(1,2)', '[1]', '2'),
		('A([B,C],[D,E])', '[0,0]', 'B'),
		('A([B,C],[D,E])', '[1,0]', 'C'),
		('A([B,C],[D,E])', '[0,1]', 'D'),
		('A([B,C],[D,E])', '[1,1]', 'E'),
	]

	def testProject(self):
		self.checkTransformation(
			path.Project,
			self.projectTestCases
		)

	pathTestCases = [
		('1', '[]', 'X(1)'),
		('[1,2]', '[]', 'X([1,2])'),
		('[1,2]', '[0]', '[X(1),2]'),
		('[1,2]', '[1]', '[1,X(2)]'),
		('C(1,2)', '[]', 'X(C(1,2))'),
		('C(1,2)', '[0]', 'C(X(1),2)'),
		('C(1,2)', '[1]', 'C(1,X(2))'),
		('A([B,C],[D,E])', '[0,1]', 'A([B,C],[X(D),E])'),
		('A([B,C],[D,E])', '[1,0]', 'A([B,X(C)],[D,E])'),
	]

	def testSubTerm(self):
		self.checkTransformation(
			lambda p: path.SubTerm(Rule('x -> X(x)'), p),
			self.pathTestCases
		)

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

	def testRange(self):
		for inputStr, start, end, expectedResultStr in self.rangeTestCases:
			input = self.factory.parse(inputStr)
			expectedResult = self.factory.parse(expectedResultStr)

			result = path.Range(lists.Map(Rule('x -> X(x)')), start, end)(input)

			self.failUnlessEqual(result, expectedResult)


class TestLists(TestMixin, unittest.TestCase):

	mapTestCases = (
		[ident, fail, Rule('x -> X(x)'), match.Int(1)],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', 'FAILURE', '[X(1)]', '[1]'],
			'[1,2]': ['[1,2]', 'FAILURE', '[X(1),X(2)]', 'FAILURE'],
		}
	)

	def testMap(self):
		self._testMetaTransf(lists.Map, self.mapTestCases)

	filterTestCases = (
		[ident, fail, Rule('x -> X(x)'), match.Int(2)],
		{
			'[]': ['[]', '[]', '[]', '[]'],
			'[1]': ['[1]', '[]', '[X(1)]', '[]'],
			'[1,2]': ['[1,2]', '[]', '[X(1),X(2)]', '[2]'],
			'[1,2,3]': ['[1,2,3]', '[]', '[X(1),X(2),X(3)]', '[2]'],
		}
	)

	def testFilter(self):
		self._testMetaTransf(lists.Filter, self.filterTestCases)
		self._testMetaTransf(lists.FilterR, self.filterTestCases)

	fetchTestCases = (
		[ident, fail, Rule('X -> Y')],
		{
			'[]': ['FAILURE', 'FAILURE', 'FAILURE'],
			'[X]': ['X', 'FAILURE', 'Y'],
			'[X,A]': ['X', 'FAILURE', 'Y'],
			'[A,X]': ['A', 'FAILURE', 'Y'],
			'[X{1},X{2}]': ['X{1}', 'FAILURE', 'Y'],
		}
	)

	def testFetch(self):
		self._testMetaTransf(lists.Fetch, self.fetchTestCases)

	# TODO: testOne

	def testSplit(self):
		self._testTransf(
			lists.Split(Rule('X -> Y')),
			(
				('[A,B,C]', 'FAILURE'),
				('[X,A,B,C]', '[[],[A,B,C]]'),
				('[A,X,B,C]', '[[A],[B,C]]'),
				('[A,B,X,C]', '[[A,B],[C]]'),
				('[A,B,C,X]', '[[A,B,C],[]]'),
			)
		)

	def testSplitBefore(self):
		self._testTransf(
			lists.SplitBefore(Rule('X -> Y')),
			(
				('[A,B,C]', 'FAILURE'),
				('[X,A,B,C]', '[[],[Y,A,B,C]]'),
				('[A,X,B,C]', '[[A],[Y,B,C]]'),
				('[A,B,X,C]', '[[A,B],[Y,C]]'),
				('[A,B,C,X]', '[[A,B,C],[Y]]'),
			)
		)

	def testSplitAfter(self):
		self._testTransf(
			lists.SplitAfter(Rule('X -> Y')),
			(
				('[A,B,C]', 'FAILURE'),
				('[X,A,B,C]', '[[Y],[A,B,C]]'),
				('[A,X,B,C]', '[[A,Y],[B,C]]'),
				('[A,B,X,C]', '[[A,B,Y],[C]]'),
				('[A,B,C,X]', '[[A,B,C,Y],[]]'),
			)
		)

	def testSplitKeep(self):
		self._testTransf(
			lists.SplitKeep(Rule('X -> Y')),
			(
				('[A,B,C,D]', 'FAILURE'),
				('[X,A,B,C,D]', '[[],Y,[A,B,C,D]]'),
				('[A,X,B,C,D]', '[[A],Y,[B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],Y,[C,D]]'),
				('[A,B,C,X,D]', '[[A,B,C],Y,[D]]'),
				('[A,B,C,D,X]', '[[A,B,C,D],Y,[]]'),
			)
		)

	def testSplitAll(self):
		self._testTransf(
			lists.SplitAll(Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[],[A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],[C,D]]'),
				('[A,X,B,X,C]', '[[A],[B],[C]]'),
				('[X,A,B,C,X]', '[[],[A,B,C],[]]'),
			)
		)

	def _testSplitAllBefore(self):
		self._testTransf(
			lists.SplitAllBefore(Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[],[Y,A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],[Y,C,D]]'),
				('[A,X,B,X,C]', '[[A],[Y,B],[Y,C]]'),
				('[X,A,B,C,X]', '[[],[Y,A,B,C],[Y]]'),
			)
		)

	def testSplitAllAfter(self):
		self._testTransf(
			lists.SplitAllAfter(Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[Y],[A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B,Y],[C,D]]'),
				('[A,X,B,X,C]', '[[A,Y],[B,Y],[C]]'),
				('[X,A,B,C,X]', '[[Y],[A,B,C,Y],[]]'),
			)
		)

	def testSplitAllKeep(self):
		self._testTransf(
			lists.SplitAllKeep(Rule('X -> Y')),
			(
				('[A,B,C,D]', '[[A,B,C,D]]'),
				('[X,A,B,C,D]', '[[],Y,[A,B,C,D]]'),
				('[A,B,X,C,D]', '[[A,B],Y,[C,D]]'),
				('[A,X,B,X,C]', '[[A],Y,[B],Y,[C]]'),
				('[X,A,B,C,X]', '[[],Y,[A,B,C],Y,[]]'),
			)
		)


if __name__ == '__main__':
	unittest.main()

