'''Refactor and view menus.'''


import gtk

import refactoring

from ui import inputter


class RefactorMenu(gtk.Menu):

	refactoring_factory = refactoring.Factory()

	def __init__(self, model):
		gtk.Menu.__init__(self)
		self.model = model
		self.populate()

	def populate(self):
		names = self.refactoring_factory.refactorings.keys()
		names.sort()
		for name in names:
			refactoring = self.refactoring_factory.refactorings[name]
			menuitem = gtk.MenuItem(refactoring.name())
			menuitem.connect("realize", self.on_menuitem_realize, refactoring)
			menuitem.connect("activate", self.on_menuitem_activate, refactoring)
			menuitem.show()
			self.append(menuitem)

		menuitem = gtk.SeparatorMenuItem()
		menuitem.show()
		self.append(menuitem)

		menuitem = gtk.MenuItem("Reload All Refactorings")
		menuitem.connect("activate", self.on_reload_activate)
		menuitem.show()
		self.append(menuitem)

	def on_menuitem_realize(self, menuitem, refactoring):
		term = self.model.get_term()
		selection = self.model.get_selection()
		if refactoring.applicable(term, selection):
			menuitem.set_state(gtk.STATE_NORMAL)
		else:
			menuitem.set_state(gtk.STATE_INSENSITIVE)

	def on_menuitem_activate(self, menuitem, refactoring):
		# Ask user input
		args = refactoring.input(
			self.model.get_term(),
			self.model.get_selection(),
		)

		self.model.apply_refactoring(refactoring, args)

	def on_reload_activate(self, dummy):
		print "Reloading all refactorings..."
		for menuitem in self.get_children():
			self.remove(menuitem)
		self.refactoring_factory.load()
		self.populate()


import termview
import dotview


class ViewMenu(gtk.Menu):

	viewfactories = [
		termview.TermViewFactory(),
		dotview.CfgViewFactory(),
	]

	def __init__(self, model):
		gtk.Menu.__init__(self)
		self.model = model

		for viewfactory in self.viewfactories:
			menuitem = gtk.MenuItem(viewfactory.get_name())
			menuitem.connect("realize", self.on_menuitem_realize, viewfactory)
			menuitem.connect("activate", self.on_menuitem_activate, viewfactory)
			menuitem.show()
			self.append(menuitem)

	def on_menuitem_realize(self, menuitem, viewfactory):
		if viewfactory.can_create(self.model):
			menuitem.set_state(gtk.STATE_NORMAL)
		else:
			menuitem.set_state(gtk.STATE_INSENSITIVE)

	def on_menuitem_activate(self, menuitem, viewfactory):
		viewfactory.create(self.model)


def PopupMenu(model):

	menu = gtk.Menu()

	#menuitem = gtk.MenuItem()
	#menuitem.show()
	#menu.prepend(menuitem)

	menuitem = gtk.MenuItem("View")
	viewmenu = ViewMenu(model)
	menuitem.set_submenu(viewmenu)
	menuitem.show()
	menu.prepend(menuitem)

	menuitem = gtk.MenuItem("Refactor")
	refactormenu = RefactorMenu(model)
	menuitem.set_submenu(refactormenu)
	menuitem.show()
	menu.prepend(menuitem)

	return menu


