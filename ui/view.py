'''View abstraction and discovery.'''


class View:
	'''Base class for model views.'''

	def __init__(self, model):
		self.model = model

	def get_name(self):
		'''Get the name of this view.'''
		raise NotImplementedError

	def destroy(self):
		'''Destroy this view.'''
		raise NotImplementedError


class ViewFactory:
	'''Base class for model views factories.'''

	def __init__(self):
		pass

	def get_name(self):
		'''The name of the created views.'''
		raise NotImplementedError

	def can_create(self, model):
		'''Whether a view can be created for this model.'''
		raise NotImplementedError

	def create(self, model):
		'''Create a view for this model.'''
		raise NotImplementedError


def main(cls):
	'''Simple main function to test views.'''

	import sys
	import gtk
	import aterm.factory
	import ui.model

	factory = aterm.factory.factory
	if len(sys.argv) > 1:
		fp = file(sys.argv[1], 'rb')
	else:
		fp = sys.stdin
	term = factory.readFromTextFile(fp)
	model = ui.model.Model()
	model.set_term(term)
	view = cls(model)
	view.connect('destroy', gtk.main_quit)
	gtk.main()