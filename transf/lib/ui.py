'''User data input transformations.'''


import sys

from transf import exception
from transf import transformation
from transf.lib import build


class Inputter(object):
	'''Base class for all user data inputters.'''

	def inputStr(self, title, text):
		raise NotImplementedError

	# TODO: other kind of inputs
	# TODO: dinamically generate complex dialogs from a term
	# description


class CliInputter(Inputter):
	'''Simple command-line-interface inputter.'''

	def inputStr(self, title, text):
		sys.stdout.write(title + '\n')
		sys.stdout.write(text + '\n')
		return sys.stdin.readline()[:-1]


inputter = Inputter()


class Str(transformation.Transformation):

	def __init__(self, title=None, text=None):
		transformation.Transformation.__init__(self)
		if title is None:
			self.title = build.empty
		else:
			self.title = title
		if text is None:
			self.text = build.empty
		else:
			self.text = text

	def apply(self, trm, ctx):
		title = self.title.apply(trm, ctx)
		text = self.text.apply(trm, ctx)
		result = inputter.inputStr(title.value, text.value)
		if result is None:
			raise exception.Failure
		else:
			return trm.factory.makeStr(result)
