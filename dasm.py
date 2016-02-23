#!/usr/bin/env python

import sys
import optparse
import subprocess
import re


def disassemble(infile, outfp, objdump='objdump', verbose = True):

	command_line = [
		'objdump',
		'--disassemble',
		'--disassemble-zeroes',
		'--disassembler-options=att,suffix',
		#'--prefix-addresses',
		'--no-show-raw-insn',
		'--wide',
		infile
	]
	p = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=False)
	#print p.communicate()[0]; return
	infp = p.stdout

	it = iter(infp)
	for line in it:
		# TODO: handle other sections too
		if line == "Disassembly of section .text:\n":
			break

	insns = []
	addrs = {}
	for line in it:
		if not line:
			break
		line = line[:-1]
		if not line:
			continue
		if line.startswith("Disassembly of section "):
			break

		line = re.sub(r"([0-9A-Fa-f]+) <([._@A-Za-z][_@A-Za-z]*)>", r"\2", line)
		line = re.sub(r"([0-9A-Fa-f]+) <([^>]*)>", r"0x\1", line)

		addr, insn = [part.strip() for part in line.split(":", 1)]
		if insn == "(bad)":
			continue
		try:
			intaddr = int(addr, 16)
		except ValueError:
			pass
		else:
			addrs[intaddr] = "loc" + addr
		insns.append((addr, insn))

	used_addrs = set()

	def repl(mo):
		addr = mo.group()
		intaddr = int(addr,16)
		try:
			addr = addrs[intaddr]
		except KeyError:
			pass
		else:
			used_addrs.add(intaddr)
		return addr

	for addr, insn in insns:
		insn = re.sub(r'\b0[xX]([0-9a-fA-F]+)\b', repl, insn)
		try:
			intaddr = int(addr, 16)
		except ValueError:
			outfp.write("%s:\n" % (addr,))
		else:
			if intaddr in used_addrs:
				outfp.write("%s:\n" % (addrs[intaddr],))
		outfp.write("\t%s\n" % (insn,))


def main():
	parser = optparse.OptionParser(
		usage = "\n\t%prog [options] executable ...",
		version = "%prog 1.0")
	parser.add_option(
		'--objdump',
		type = "string", dest = "objdump", default = "objdump",
		help = "path to objdump executable")
	parser.add_option(
		'-o', '--output',
		type = "string", dest = "output",
		help = "specify output assembly file")
	parser.add_option(
		'-v', '--verbose',
		action = "count", dest = "verbose", default = 1,
		help = "show extra information")
	parser.add_option(
		'-q', '--quiet',
		action = "store_const", dest = "verbose", const = 0,
		help = "no extra information")
	(options, args) = parser.parse_args(sys.argv[1:])

	for arg in args:
		if options.output is None:
		#	root, ext = os.path.splitext(arg)
		#	fpout = file(root + '.s', 'wt')
		#elif options.output is '-':
			fpout = sys.stdout
		else:
			fpout = file(options.output, 'wt')

		disassemble(arg, fpout, options.objdump, options.verbose)


if __name__ == '__main__':
	main()

