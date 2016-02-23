'''Common transformations.'''


from transf import util
from transf import lib as trf
import ir.match


def Traverse(subterms, down = trf.base.ident, up = trf.base.ident, stop = trf.base.ident, Enter = trf.base.ident, Leave = trf.base.ident):
	'''Generic traversal.'''
	traverse = subterms
	if Leave is not trf.base.ident:
		traverse = Leave(traverse)
	if stop is not trf.base.ident:
		traverse = trf.combine.Choice(stop, traverse)
	if up is not trf.base.ident:
		traverse = trf.combine.Composition(traverse, up)
	if down is not trf.base.ident:
		traverse = trf.combine.Composition(down, traverse)
	if Enter is not trf.base.ident:
		traverse = Enter(traverse)
	return traverse


def Module(stmts = trf.base.ident, **kargs):
	return Traverse(
		trf.congruent.Appl('Module', (stmts,)),
		**kargs
	)


def Function(type = trf.base.ident, name = trf.base.ident, args = trf.base.ident, stmts = trf.base.ident, **kargs):
	return Traverse(
		trf.congruent.Appl('Function', (type, name, args, stmts)),
		**kargs
	)


def While(cond = trf.base.ident, stmt = trf.base.ident, **kargs):
	return Traverse(
		trf.congruent.Appl('While', (cond, stmt)),
		**kargs
	)


def DoWhile(cond = trf.base.ident, stmt = trf.base.ident, **kargs):
	return Traverse(
		trf.congruent.Appl('DoWhile', (cond, stmt)),
		**kargs
	)


def If(cond = trf.base.ident, true = trf.base.ident, false = trf.base.ident, **kargs):
	return Traverse(
		trf.congruent.Appl('If', (cond, true, false)),
		**kargs
	)


def Block(stmts = trf.base.ident, **kargs):
	return Traverse(
		trf.congruent.Appl('Block', (stmts,)),
		**kargs
	)


def Stmt(stmt, stmts, default, **kargs):
	return Traverse(
		ir.match.aBlock **Block(stmts)**
		ir.match.anIf **If(trf.base.ident, stmt, stmt)**
		ir.match.aWhile **While(trf.base.ident, stmt)**
		ir.match.aDoWhile **DoWhile(trf.base.ident, stmt)**
		ir.match.aFunction **Function(trf.base.ident, trf.base.ident, trf.base.ident, stmts)**
		ir.match.aModule **Module(stmts)**
		default,
		**kargs
	)

def AllStmts(**kargs):
	stmt = util.Proxy()
	stmts = trf.lists.Map(stmt)
	stmt.subject = Stmt(stmt, stmts, trf.base.ident, **kargs)
	return stmt


def AllStmtsBU(up):
	return AllStmts(up = up)


def OneStmt(pre, post = trf.base.ident):
	stmt = util.Proxy()
	stmts = trf.lists.One(stmt)
	stmt.subject = pre ** post ** Stmt(stmt, stmts, trf.base.fail)
	return stmt


def AllGlobalStmts(operand):
	return Module(
		trf.lists.Map(operand)
	)

def OneGlobalStmt(operand):
	return Module(
		trf.lists.One(operand)
	)

def OneFunction(operand, type = trf.base.ident, name = trf.base.ident, args = trf.base.ident, stmts = trf.base.ident):
	return OneGlobalStmt(
		ir.match.Function(type, name, args, stmts),
		operand
	)


def main():
	import aterm.factory
	import sys
	factory = aterm.factory.factory
	for arg in sys.argv[1:]:
		print "* Reading aterm"
		term = factory.readFromTextFile(file(arg, 'rt'))
		#print ( pprint2.module * renderBox )(term)
		#print

		#print AllStmts(up = trf.debug.Dump() * trf.annotation.Set('X')) (term)
		print OneStmt(trf.debug.Dump() * ir.match.aLabel * trf.annotation.Set('X')) (term)


if __name__ == '__main__':
	main()
