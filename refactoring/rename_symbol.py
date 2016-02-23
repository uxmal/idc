"""Rename Symbol"""


from transf import parse
import ir.path


parse.Transfs(r'''

applicable =
	ir.path.Applicable(
		ir.path.projectSelection => Sym(_)
	)

input =
	ir.path.Input2(
		ir.path.projectSelection => Sym(src) ;
		ui.Str(!"Rename Symbol", !"Destination symbol?") => dst ;
		![src, dst]
	)

apply =
	( [root, [src, dst]] -> root ) ;
	AllTD((
		~Sym(< src -> dst >) |
		~Arg(_, < src -> dst >)
	))


doTestApply =
	apply [<id>, ["a", "b"]]

testNoRename =
	doTestApply Sym("c") => Sym("c")

testRename =
	doTestApply Sym("a") => Sym("b")

testRenameInList =
	doTestApply [Sym("a"),Sym("c")] => [Sym("b"),Sym("c")]

testRenameInAppl =
	doTestApply C(Sym("a"),Sym("c")) => C(Sym("b"),Sym("c"))

''')
