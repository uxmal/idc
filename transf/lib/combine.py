'''Transformation combinators.'''


from transf import exception
from transf import transformation
from transf import operate
from transf.lib import base


class _Not(operate.Unary):

	__slots__ = []

	def apply(self, term, ctx):
		try:
			self.operand.apply(term, ctx)
		except exception.Failure:
			return term
		else:
			raise exception.Failure

def Not(operand):
	'''Fail if a transformation applies.'''
	if operand is base.ident:
		return base.fail
	if operand is base.fail:
		return base.ident
	if type(operand) is _Not:
		return operand.operand
	return _Not(operand)


class _Try(operate.Unary):

	__slots__ = []

	def apply(self, term, ctx):
		try:
			return self.operand.apply(term, ctx)
		except exception.Failure:
			return term

def Try(operand):
	'''Attempt a transformation, otherwise return the term unmodified.'''
	if operand is base.ident:
		return operand
	if operand is base.fail:
		return base.ident
	return _Try(operand)


class _Where(operate.Unary):

	__slots__ = []

	def apply(self, term, ctx):
		self.operand.apply(term, ctx)
		return term

def Where(operand):
	'''Succeeds if the transformation succeeds, but returns the original term.'''
	if operand is base.ident:
		return base.ident
	if operand is base.fail:
		return base.ident
	if type(operand) is _Where:
		return operand
	if type(operand) is _Try:
		return base.ident
	return _Where(operand)


class _Composition(operate.Binary):

	__slots__ = []

	def apply(self, term, ctx):
		term = self.loperand.apply(term, ctx)
		return self.roperand.apply(term, ctx)

def Composition(loperand, roperand):
	'''Transformation composition.'''
	assert isinstance(loperand, transformation.Transformation)
	assert isinstance(roperand, transformation.Transformation)
	if loperand is base.ident:
		return roperand
	if roperand is base.ident:
		return loperand
	if loperand is base.fail:
		return base.fail
	while type(loperand) is _Composition:
		roperand = _Composition(loperand.roperand, roperand)
		loperand = loperand.loperand
	return _Composition(loperand, roperand)


class _Choice(operate.Binary):

	__slots__ = []

	def apply(self, term, ctx):
		try:
			return self.loperand.apply(term, ctx)
		except exception.Failure:
			return self.roperand.apply(term, ctx)

def Choice(loperand, roperand):
	'''Attempt the first transformation, transforming the second on failure.'''
	assert isinstance(loperand, transformation.Transformation)
	assert isinstance(roperand, transformation.Transformation)
	if loperand is base.ident:
		return base.ident
	if loperand is base.fail:
		return roperand
	if roperand is base.ident:
		return Try(loperand)
	if roperand is base.fail:
		return loperand
	while type(loperand) is _Choice:
		roperand = _Choice(loperand.roperand, roperand)
		loperand = loperand.loperand
	return _Choice(loperand, roperand)


class _GuardedChoice(operate.Ternary):

	__slots__ = []

	def apply(self, term, ctx):
		try:
			term = self.operand1.apply(term, ctx)
		except exception.Failure:
			return self.operand3.apply(term, ctx)
		else:
			return self.operand2.apply(term, ctx)

def GuardedChoice(operand1, operand2, operand3):
	'''If operand1 succeeds then operand2 is applied, otherwise operand3 is
	applied. If operand2 fails, the complete expression fails; no backtracking to
	operand3 takes place.
	'''
	if operand1 is base.ident:
		return operand2
	if operand1 is base.fail:
		return operand3
	if operand2 is base.ident:
		return Choice(operand1, operand3)
	if operand3 is base.fail:
		return Composition(operand1, operand2)
	return _GuardedChoice(operand1, operand2, operand3)


def UndeterministicChoice(operands):
	'''Chooses one of the operand transformations such that the one it chooses
	succeeds. If all operand transformations fail, then the choice fails as
	well. Operationally, the operand transformations are tried, by an
	unspecified order.
	'''
	return operate.Nary(operands, Choice, base.fail)


class _If(operate.Binary):

	__slots__ = []

	def apply(self, term, ctx):
		try:
			self.loperand.apply(term, ctx)
		except exception.Failure:
			return term
		else:
			return self.roperand.apply(term, ctx)

def If(loperand, roperand):
	'''If the first transformation succeeds, then applies the second
	transformation. Otherwise, return the input term unmodified.
	'''
	if loperand is base.ident:
		return roperand
	if loperand is base.fail:
		return base.ident
	if roperand is base.ident:
		return Where(loperand)
	if roperand is base.fail:
		return Not(loperand)
	return _If(loperand, roperand)


class _IfElse(operate.Ternary):

	__slots__ = []

	def apply(self, term, ctx):
		try:
			self.operand1.apply(term, ctx)
		except exception.Failure:
			return self.operand3.apply(term, ctx)
		else:
			return self.operand2.apply(term, ctx)

def IfElse(operand1, operand2, operand3):
	'''If the first transformation succeeds, then apply the second
	transformation. Otherwise, applies the third transformation.
	'''
	if operand1 is base.ident:
		return operand2
	if operand1 is base.fail:
		return operand3
	if operand3 is base.fail:
		return If(operand1, operand2)
	return _IfElse(operand1, operand2, operand3)


class _IfElifElse(transformation.Transformation):

	__slots__ = ['clauses', 'otherwise']

	def __init__(self, clauses, otherwise):
		transformation.Transformation.__init__(self)
		self.clauses = clauses
		self.otherwise = otherwise

	def apply(self, term, ctx):
		for if_cond, if_then in self.clauses:
			try:
				if_cond.apply(term, ctx)
			except exception.Failure:
				pass
			else:
				return if_then.apply(term, ctx)
		return self.otherwise.apply(term, ctx)

def IfElifElse(clauses, otherwise = None):
	'''Nested if-then-else combinator.

	@param clauses: sequence of (premise, consequence) transformation tuples
	to be tried in order.
	@param otherwise: optional transformation to be applied if all the above
	premises fail.
	'''
	if otherwise is None:
		otherwise = base.ident
	if len(clauses) == 0:
		return otherwise
	if len(clauses) == 1:
		((cond, true),) = clauses
		return IfElse(cond, true, otherwise)
	return _IfElifElse(clauses, otherwise)


class _Switch(transformation.Transformation):

	__slots__ = ['expr', 'cases', 'otherwise']

	def __init__(self, expr, cases, otherwise):
		transformation.Transformation.__init__(self)
		self.expr = expr
		self.cases = cases
		self.otherwise = otherwise

	def apply(self, term, ctx):
		switch_term = self.expr.apply(term, ctx)
		try:
			action = self.cases[switch_term]
		except KeyError:
			return self.otherwise.apply(term, ctx)
		else:
			return action.apply(term, ctx)

def Switch(expr, cases, otherwise = None):
	'''Switch combination.

	@param cases: sequence of (match term, consequence transformation)
	tuples; order is irrelevant.
	@param otherwise: optional transformation to be applied if the term does
	not match any of the input cases.
	'''
	if otherwise is None:
		otherwise = base.fail
	_cases = {}
	if len(cases) == 0:
		return Composition(Where(expr), otherwise)
	for terms, action in cases:
		if not isinstance(terms, (tuple, list)):
			terms = (terms,)
		for term in terms:
			if term in _cases:
				raise ValueError('duplicate case', term)
			_cases[term] = action
	return _Switch(expr, _cases, otherwise)
