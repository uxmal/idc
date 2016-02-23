#!/usr/bin/env python


import sys
import optparse
import os
import os.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..')))

import aterm.factory
import box
import ir.path
import ir.check
import ir.pprint
import machine.pentium


factory = aterm.factory.factory


def pretty_print(term):
	boxes = ir.pprint.module(term)
	if sys.stderr.isatty() and sys.platform != 'win32':
		formatter = box.AnsiTextFormatter
	else:
		formatter = box.TextFormatter
	sys.stderr.write(box.stringify(boxes, formatter))


def translate(fpin, fpout, verbose = True):
	if verbose:
		sys.stderr.write('* %s *\n' % fpin.name)
		sys.stderr.write('\n')

	if verbose:
		sys.stderr.write('** Assembly **\n')
		sys.stderr.write(fpin.read())
		sys.stderr.write('\n')
		fpin.seek(0)

	mach = machine.pentium.Pentium()
	term = mach.load(factory, fpin)
	ir.check.module(term)

	if verbose:
		sys.stderr.write('** Low-level IR **\n')
		if verbose > 1:
			sys.stderr.write(str(term) + '\n')
		pretty_print(term)
		sys.stderr.write('\n')

	term = mach.translate(term)
	ir.check.module(term)

	if verbose:
		sys.stderr.write('** Translated IR **\n')
		if verbose > 1:
			sys.stderr.write(str(term) + '\n')
		pretty_print(term)
		sys.stderr.write('\n')

		sys.stderr.write('\n')

	term = ir.path.annotate(term)

	term.writeToTextFile(fpout)


def main():
	parser = optparse.OptionParser(
		usage = "\n\t%prog [options] file ...",
		version = "%prog 1.0")
	parser.add_option(
		'-o', '--output',
		type = "string", dest = "output",
		help = "specify output file")
	parser.add_option(
		'-v', '--verbose',
		action = "count", dest = "verbose", default = 1,
		help = "show extra information")
	parser.add_option(
		'-q', '--quiet',
		action = "store_const", dest = "verbose", const = 0,
		help = "no extra information")
	parser.add_option(
		'-p', '--profile',
		action = "store_true", dest = "profile", default = False,
		help = "collect profiling information")
	(options, args) = parser.parse_args(sys.argv[1:])

	for arg in args:
		fpin = file(arg, 'rt')

		if options.output is None:
			root, ext = os.path.splitext(arg)
			fpout = file(root + '.aterm', 'wt')
		elif options.output is '-':
			fpout = sys.stdout
		else:
			fpout = file(options.output, 'wt')

		if options.profile:
			import hotshot
			root, ext = os.path.splitext(arg)
			profname = root + '.prof'
			prof = hotshot.Profile(profname, lineevents=0)
			prof.runcall(translate, fpin, fpout, options.verbose)
			prof.close()
		else:
			translate(fpin, fpout, options.verbose)


if __name__ == '__main__':
	main()

