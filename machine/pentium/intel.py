'''Intel Assembly parser.'''


from pyparsing import *


__all__ = ['parser']



dotSymbol = Word('.', alphanums + '_.$')
symbol = Word(alphas + '_', alphanums + '_.$')
symbol.setName("symbol")

binary = Regex('0[bB][01]+')
#hexadecimal = Regex('0[xX][0-9a-fA-F]+')
hexadecimal = Regex('[0-9][0-9a-fA-F]*h')
#octal = Word('0', nums)
decimal = Word(nums)

#number = ( binary | hexadecimal | octal | decimal )
number = ( binary | hexadecimal | decimal ).setName("number")

atom = symbol | number
memory = Group(Optional(oneOf("byte word dword qword") + Literal("ptr")) +  "[" + atom + "]")
operand = atom | memory

opcode = symbol

label = symbol + ':'

eol = Suppress(White("\n"))
eol.setName("eol")

stmt = ZeroOrMore(label) + opcode + delimitedList(operand)
stmt.setName("stmt")
#stmt.setDebug()

segmentDirective = symbol + Literal("segment") + restOfLine
publicDirective = Literal("public") + symbol
alignDirective = Literal("align") + number

directive = (segmentDirective | publicDirective | alignDirective)
directive.setName("directive")


line = Optional(Group(directive | stmt))
line.setName("line")
#line.setDebug()

asm = ZeroOrMore(line) #+ stringEnd

comment = Literal(';') + restOfLine
line.ignore(comment)


if __name__ == '__main__':
	import sys
	import pprint
	for arg in sys.argv[1:]:
		for l in open(arg,"rt"):
			print line.parseString(l)
