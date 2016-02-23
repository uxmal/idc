'''Path/selection related transformations.'''


from transf import parse
import ir.match


parse.Transfs(r'''

#######################################################################
# Path annotation

# Only annotate term applications
annotate = path.Annotate(
	match.ApplNames(`
		ir.match.stmtNames +
		ir.match.exprNames +
		ir.match.typeNames
	`)
)

deannotate = path.deannotate


#######################################################################
# Selection

shared selection

Applicable(t) =
	with selection in
		?[root, selection] ;
		!root ;
		t
	end

Input(t) =
	with selection in
		?[root, selection] ;
		!root ;
		# annotate ;
		t ;
		![selection, *<id>]
	end

Input2(t) =
	with selection in
		?[root, selection] ;
		!root ;
		# annotate ;
		t
	end

Apply(t) =
	with selection in
		?[root, [selection, *args]] ;
		![root, args] ;
		t ;
		deannotate
	end



WithSelection(s, x) = with selection in x where selection := s end



projectSelection = path.Project(!selection)

MatchSelectionTo(s) = projectSelection ; s


#######################################################################
# Selection context

getSelection = !selection

isSelected =
	Where(
		path.get ;
		path.Equals(getSelection)
	)

inSelection =
	Where(
		path.get ;
		path.Contained(getSelection)
	)

hasSelection =
	Where(
		path.get ;
		path.Contains(getSelection)
	)

''')
