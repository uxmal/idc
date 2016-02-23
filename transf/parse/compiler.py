"""Translates the transformation describing aterms into the
respective transformation objects."""


from sets import Set as set
from aterm import walker


# pylint: disable-msg=R0201


class SemanticException(Exception):

	pass


# term operations
ASSIGN, MATCH, BUILD, CONGRUENT = range(4)


class Compiler(walker.Walker):

	def __init__(self, debug=False):
		self.debug = debug

		self.stmts = []
		self.indent = 0

		self.globals = set()
		self.args = set()
		self.locals = set()

	def stmt(self, s):
		self.stmts.append('\t' * self.indent + s)


	definitions = walker.Dispatch('definitions')

	def definitionsDefs(self, tdefs):
		for tdef in tdefs:
			self.predefine(tdef)
		self.stmt('')
		for tdef in tdefs:
			self.define(tdef)
			self.stmt('')

		return "\n".join(self.stmts)


	predefine = walker.Dispatch('predefine')

	def predefineVarDef(self, n, t):
		n = self.id(n)
		t = self.type(t)
		if t is not None:
			self.stmt("%s = %s(%r)" % (n, t, n))
		self.globals.add(n)

	def type(self, t):
		t = self._str(t)
		if t == "term":
			return "transf.types.term.Term"
		if t == "table":
			return "transf.types.table.Table"
		if t == "extern":
			return None
		return t

	def predefineTransfDef(self, n, t):
		n = self.id(n)
		if self.debug:
			self.stmt("%s = transf.lib.debug.Trace(None, name=%r)" % (n, n))
		else:
			self.stmt("%s = transf.util.Proxy()" % (n,))

	def predefineMacroDef(self, n, a, t):
		pass


	define = walker.Dispatch('define')

	def defineVarDef(self, n, t):
		pass

	def type(self, t):
		t = self._str(t)
		if t == "term":
			return "transf.types.term.Term"
		if t == "table":
			return "transf.types.table.Table"
		if t == "extern":
			return None
		return t

	def defineTransfDef(self, n, t):
		self.args = set()
		n = self.id(n)
		t = self.doTransf(n, t)
		self.stmt("%s.subject = %s" % (n, t))
		if self.locals:
			self.stmt("del %s" % ",".join([self.local(var) for var in self.locals]))
		self.args = set()

	def defineMacroDef(self, n, a, t):
		n = self.id(n)
		a = self.id_list(a)
		self.args = set(a)

		a = ",".join(a)
		try:
			n.index(".")
		except ValueError:
			self.stmt("def %s(%s):" % (n, a))
			self.indent += 1
			t = self.doTransf(n, t)
			if self.debug:
				t = "transf.lib.debug.Trace(%s, %r)" % (t, n)
			self.stmt("return %s" % t)
			self.indent -= 1
		else:
			# XXX: hack for proxy to work
			self.stmt("def _tmp(%s):" % a)
			self.indent += 1
			t = self.doTransf(n, t)
			if self.debug:
				t = "transf.lib.debug.Trace(%s, %r)" % (t, n)
			self.stmt("return %s" % t)
			self.indent -= 1
			self.stmt("%s = _tmp" % n)
		self.args = set()

	def doTransf(self, n, t):
		self.locals = set()
		# TODO: pre-collect the vars
		t = self.transf(t)
		vs = self.locals
		if vs:
			vs = "[" + ",".join([self.local(v) for v in vs]) + "]"
			t =  "transf.lib.scope.Scope(%s, %s)" % (vs, t)
		return t


	transf = walker.Dispatch('transf')

	def transfIdent(self):
		return "transf.lib.base.ident"

	def transfFail(self):
		return "transf.lib.base.fail"

	def transfMatch(self, t):
		return self.match(t)

	def transfBuild(self, t):
		return self.build(t)

	def transfCongruent(self, t):
		return self.congruent(t)

	def transfComposition(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return "transf.lib.combine.Composition(%s, %s)" % (l, r)

	def transfChoice(self, o):
		# FIXME: insert a variable scope here
		o = "[" + ",".join(["%s" % self.transf(_o) for _o in o]) + "]"
		return "transf.lib.combine.UndeterministicChoice(%s)" % o

	def transfLeftChoice(self, l, r):
		l = self.transf(l)
		r = self.transf(r)
		return "transf.lib.combine.Choice(%s, %s)" % (l, r)

	def transfGuardedChoice(self, l, m, r):
		l = self.transf(l)
		m = self.transf(m)
		r = self.transf(r)
		return "transf.lib.combine.GuardedChoice(%s, %s, %s)" % (l, m, r)

	def transfTransf(self, n):
		n = self.idRef(n)
		return n

	def transfMacro(self, i, a):
		n = self.idRef(i)
		a = ",".join(map(self.transf, a))
		return "%s(%s)" % (n, a)

	def transfRule(self, m, b):
		m = self.match(m)
		b = self.build(b)
		return "transf.lib.combine.Composition(%s, %s)" % (m, b)

	def transfRuleIf(self, m, b, w):
		m = self.match(m)
		b = self.match(b)
		w = self.transf(w)
		return "transf.lib.combine.Composition(%s, transf.lib.combine.If(%s, %s))" % (m, w, b)

	def transfWhere(self, t, w):
		t = self.transf(t)
		w = self.transf(w)
		return "transf.lib.combine.Composition(transf.lib.combine.Where(%s), %s)" % (w, t)

	def transfApplyMatch(self, t, m):
		t = self.transf(t)
		m = self.match(m)
		return "transf.lib.combine.Composition(%s, %s)" % (t, m)

	def transfApplyAssign(self, l, r):
		l = self.term(l, mode = ASSIGN)
		r = self.transf(r)
		return "transf.lib.combine.Where(transf.lib.combine.Composition(%s, %s))" % (r, l)

	def transfBuildApply(self, t, b):
		t = self.transf(t)
		b = self.build(b)
		return "transf.lib.combine.Composition(%s, %s)" % (b, t)

	def transfIf(self, conds, other):
		conds = "[" + ",".join(map(self.doIfClause, conds)) + "]"
		other = self.transf(other)
		return "transf.lib.combine.IfElifElse(%s, %s)" % (conds, other)

	def doIfClause(self, t):
		c, a = t.rmatch("IfClause(_, _)")
		c = self.transf(c)
		a = self.transf(a)
		return "(%s, %s)" % (c, a)

	def transfSwitch(self, expr, cases, other):
		expr = self.transf(expr)
		cases = "[" + ",".join(map(self.doSwitchClause, cases)) + "]"
		other = self.transf(other)
		return "transf.lib.combine.Switch(%s, %s, %s)" % (expr, cases, other)

	def doSwitchClause(self, t):
		c, a = t.rmatch("SwitchCase(_, _)")
		c = "[" + ",".join(map(self.static, c)) + "]"
		a = self.transf(a)
		return "(%s, %s)" % (c, a)

	def transfJoin(self, l, r, u, i):
		u = "[" + ",".join(map(self.var, u)) + "]"
		i = "[" + ",".join(map(self.var, i)) + "]"
		l = self.transf(l)
		r = self.transf(r)
		return "transf.types.table.Join(%s, %s, %s, %s)" % (l, r, u, i)

	def transfIterate(self, o, u, i):
		u = "[" + ",".join(map(self.var, u)) + "]"
		i = "[" + ",".join(map(self.var, i)) + "]"
		o = self.transf(o)
		return "transf.types.table.Iterate(%s, %s, %s)" % (o, u, i)

	def transfRec(self, i, t):
		i = self.id(i)
		oldargs = self.args
		self.args = self.args.union([i])
		t = self.transf(t)
		self.args = oldargs
		return "transf.lib.iterate.Rec(lambda %s: %s)" % (i, t)

	def transfGlobal(self, vs, t):
		vs = self.id_list(vs)
		oldargs = self.args
		self.args = self.args.union(vs)
		t = self.transf(t)
		self.args = oldargs
		return t

	def transfScope(self, vs, t):
		# TODO: collect vars
		vs = map(self.var, vs)
		t = self.transf(t)
		if len(vs):
			vs = "[" + ",".join(vs) + "]"
			t = "transf.lib.scope.Scope(%s, %s)" % (vs, t)
		return t

	def transfWithDef(self, v, t):
		v = self.var(v)
		t = self.transf(t)
		return "transf.lib.combine.Where(transf.lib.combine.Composition(%s, %s.assign))" % (t, v)

	def transfObj(self, o):
		o = self._str(o)
		return o


	static = walker.Dispatch('static')

	def staticInt(self, i):
		i = self._int(i)
		return "aterm.factory.factory.makeInt(%r)" % i

	def staticReal(self, r):
		r = self._real(r)
		return "aterm.factory.factory.makeReal(%r)" % r

	def staticStr(self, s):
		s = self._str(s)
		return "aterm.factory.factory.makeStr(%r)" % s

	def staticNil(self):
		return "aterm.factory.factory.makeNil()"

	def staticCons(self, h, t):
		h = self.static(h)
		t = self.static(t)
		return "aterm.factory.factory.makeCons(%s, %s)" % (h, t)

	def staticCat(self, h, t):
		h = self.static(h)
		t = self.static(t)
		return "aterm.lists.concat(%s, %s)" % (h, t)

	def staticUndef(self):
		return "aterm.factory.factory.makeNil()"

	def staticAppl(self, n, a):
		n = self._str(n)
		a = self.static(a)
		return "aterm.factory.factory.makeAppl(%r, %s)" % (n, a)

	def staticApplName(self, n):
		n = self._str(n)
		return "aterm.factory.factory.makeAppl(%r)" % (n)

	def staticWildcard(self):
		raise SemanticException("wildcard in static term")

	def staticVar(self, v):
		raise SemanticException("variable in static term", v)

	def staticWrap(self, t):
		raise SemanticException("transformation in static term", t)

	def staticAnnos(self, t, a):
		t = self.static(t)
		a = self.static(a)
		return "%s.setAnnotations(%s)" % (t, a)


	def match(self, t):
		return self.term(t, mode = MATCH)

	def build(self, t):
		return self.term(t, mode = BUILD)

	def congruent(self, t):
		return self.term(t, mode = CONGRUENT)


	term = walker.Dispatch('term')

	def termInt(self, i, mode):
		i = self._int(i)
		if mode == BUILD:
			return "transf.lib.build.Int(%r)" % i
		else:
			return "transf.lib.match.Int(%r)" % i

	def termReal(self, r, mode):
		r = self._real(r)
		if mode == BUILD:
			return "transf.lib.build.Real(%r)" % r
		else:
			return "transf.lib.match.Real(%r)" % r

	def termStr(self, s, mode):
		s = self._str(s)
		if mode == BUILD:
			return "transf.lib.build.Str(%r)" % s
		else:
			return "transf.lib.match.Str(%r)" % s

	def termNil(self, mode):
		if mode == BUILD:
			return "transf.lib.build.nil"
		else:
			return "transf.lib.match.nil"

	def termCons(self, h, t, mode):
		h = self.term(h, mode)
		t = self.term(t, mode)
		if mode in (ASSIGN, MATCH):
			return "transf.lib.match.Cons(%s, %s)" % (h, t)
		elif mode == BUILD:
			return "transf.lib.build.Cons(%s, %s)" % (h, t)
		elif mode == CONGRUENT:
			return "transf.lib.congruent.Cons(%s, %s)" % (h, t)
		else:
			assert False

	def termCat(self, h, t, mode):
		if mode != BUILD:
			raise SemanticException("list concatenation only supported when building terms")
		h = self.term(h, mode)
		t = self.term(t, mode)
		return "transf.lib.lists.Concat(%s, %s)" % (h, t)

	def termAppl(self, name, args, mode):
		name = self._str(name)
		args = "[" + ",".join([self.term(arg, mode) for arg in args]) + "]"
		if mode in (ASSIGN, MATCH):
			return "transf.lib.match.Appl(%r, %s)" % (name, args)
		elif mode == BUILD:
			return "transf.lib.build.Appl(%r, %s)" % (name, args)
		elif mode == CONGRUENT:
			return "transf.lib.congruent.Appl(%r, %s)" % (name, args)

	def termApplName(self, name, mode):
		name = self._str(name)
		if mode == BUILD:
			return "transf.lib.build.Appl(%r, ())" % name
		else:
			return "transf.lib.match.ApplName(%r)" % name

	def termApplCons(self, n, a, mode):
		n = self.term(n, mode)
		a = self.term(a, mode)
		if mode in (ASSIGN, MATCH):
			return "transf.lib.match.ApplCons(%s, %s)" % (n, a)
		elif mode == BUILD:
			return "transf.lib.build.ApplCons(%s, %s)" % (n, a)
		elif mode == CONGRUENT:
			return "transf.lib.congruent.ApplCons(%s, %s)" % (n, a)

	def termWildcard(self, mode):
		return "transf.lib.base.ident"

	def termVar(self, v, mode):
		v = self.var(v)
		if mode == ASSIGN:
			return "%s.assign" % v
		elif mode == MATCH:
			return "transf.lib.match.Var(%s)" % v
		elif mode == BUILD:
			return "transf.lib.build.Var(%s)" % v
		elif mode == CONGRUENT:
			return "transf.lib.congruent.Var(%s)" % v

	def termWrap(self, t, mode):
		t = self.transf(t)
		return t

	def termAnnos(self, t, a, mode):
		t = self.term(t, mode)
		a = self.term(a, mode)
		if mode in (ASSIGN, MATCH):
			r = "transf.lib.match.Annos(%s)" % a
		elif mode == BUILD:
			r = "transf.lib.build.Annos(%s)" % a
		elif mode == CONGRUENT:
			r = "transf.lib.congruent.Annos(%s)" % a
		return "transf.lib.combine.Composition(%s, %s)" % (t, r)

	def term_Term(self, t, mode):
		# fallback to a regular transformation
		t = self.transf(t)
		return t


	collect = walker.Dispatch('collect')

	def collectVar(self, name, vars):
		name = self.id(name)
		vars.add(name)

	def collectWithDef(self, name, t, vars):
		name = self.id(name)
		vars.add(name)

	def collectGlobal(self, names, operand, vars):
		names = self.id_list(names)
		for name in names:
			vars.discard(name)
		self.collect(operand)

	def collect_List(self, elms, vars):
		for elm in elms:
			self.collect(elm, vars)

	def collect_Appl(self, name, args, vars):
		for arg in args:
			self.collect(arg, vars)

	def collect_Term(self, t, vars):
		# ignore everything else
		pass


	def id(self, i):
		return self._str(i)

	def id_list(self, l):
		return map(self.id, l)

	def idRef(self, i):
		s = self.id(i)
		parts = s.split('.')
		head = parts[0]
		tail = parts[1:]
		if head in self.locals:
			return ".".join([self.local(s)] + tail)
		else:
			return s

	def var(self, v):
		v = self.id(v)
		if v in self.globals:
			return v
		if v in self.args:
			return v
		if v in self.locals:
			return self.local(v)
		self.stmt('%s = transf.types.term.Term(%r)' %(self.local(v), v))
		self.locals.add(v)
		return self.local(v)

	def local(self, v):
		return "_" + v


