'''Symbol handling transformations.'''


from transf import parse
import ir.match


parse.Transfs('''

#######################################################################
# Local variable table

shared local as table

# TODO: detect local variables from scope rules
isReg = annotation.Has(?Reg)
isTmp = annotation.Has(?Tmp)

isLocalVar =
	ir.match.aSym ;
	(isReg + isTmp)

updateLocalVar =
	isLocalVar ;
	Where(local.set [_,_] )

updateLocalVars =
	local.clear ;
	traverse.AllTD(updateLocalVar)

EnterFunction(operand) =
	with local in
		updateLocalVars ;
		operand
	end

EnterModule(operand) = EnterFunction(operand)

''')

