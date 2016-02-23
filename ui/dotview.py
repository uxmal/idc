'''View graphs in dot-language.'''


import gtk
import gtk.gdk

import ir.cfg
import dot
from ui import xdot
from ui import view


class DotView(xdot.DotWindow, view.View):

	def __init__(self, model):
		xdot.DotWindow.__init__(self)
		view.View.__init__(self, model)

		model.connect('notify::term', self.on_term_update)

		self.connect('destroy', self.on_window_destroy)

		if model.get_term() is not None:
			self.on_term_update(model.term)

	def get_name(self, name):
		return 'Dot View'

	def set_graph(self, graph):
		dotcode = dot.stringify(graph)
		self.set_dotcode(dotcode)

	def on_term_update(self, term):
		pass

	def on_window_destroy(self, event):
		model = self.model
		model.disconnect('notify::term', self.on_term_update)

	def on_url_clicked(self, url, event):
		model = self.model
		term = model.get_term()
		factory = term.factory
		path = factory.parse(url)
		return self.on_path_clicked(path, event)

	def on_path_clicked(self, path, event):
		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
			self.model.set_selection((path, path))
		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
			self.model.set_selection((path, path))
			from ui.menus import PopupMenu
			popupmenu = PopupMenu(self.model)
			popupmenu.popup( None, None, None, event.button, event.time)
		return True


class CfgView(DotView):

	def __init__(self, model):
		DotView.__init__(self, model)
		self.set_title('Control Flow Graph')

	def on_term_update(self, term):
		graph = ir.cfg.render(term)
		self.set_graph(graph)


class CfgViewFactory(view.ViewFactory):

	def get_name(self):
		return 'Control Flow Graph'

	def can_create(self, model):
		return True

	def create(self, model):
		return CfgView(model)


if __name__ == '__main__':
	view.main(CfgView)
