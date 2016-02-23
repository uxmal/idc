"""Aterm inspector view."""


import gtk
import gobject

from ui import view

import aterm.types


class TermTreeIter:
	"""Iterator for TermTreeModel."""

	def __init__(self, path, parents, head, tail):
		self.path = path
		self.parents = parents
		self.head = head
		self.tail = tail

	def term(self):
		return self.head

	def next(self):
		if not self.tail:
			return None
		else:
			return TermTreeIter(
				self.path[:-1] + (self.path[-1] + 1,),
				self.parents,
				self.tail.head,
				self.tail.tail
			)

	def _children(self):
		term = self.head
		if aterm.types.isList(term):
			return term
		elif aterm.types.isAppl(term):
			return term.factory.makeList(term.args)
		else:
			return term.factory.makeNil()

	def children(self):
		children = self._children()
		if not children:
			return None
		else:
			return TermTreeIter(
				self.path + (0,),
				self.parents + ((self.head, self.tail),),
				children.head,
				children.tail
			)

	def has_child(self):
		children = self._children()
		return bool(children)

	def n_children(self):
		children = self._children()
		return len(children)

	def nth_child(self, n):
		children = self._children()
		if n > len(children):
			return None
		else:
			for i in range(n):
				children = children.tail
			return TermTreeIter(
				self.path + (n,),
				self.parents + ((self.head, self.tail),),
				children.head,
				children.tail
			)

	def parent(self):
		if not len(self.parents):
			return None
		else:
			return TermTreeIter(
				self.path[:-1],
				self.parents[:-1],
				self.parents[-1][0],
				self.parents[-1][1],
			)


class TermTreeModel(gtk.GenericTreeModel):
	''''Generic tree model for an aterm.'''

	def __init__(self, term):
		'''constructor for the model.  Make sure you call
		PyTreeModel.__init__'''
		gtk.GenericTreeModel.__init__(self)

		self.top = TermTreeIter((), (), term, term.factory.makeNil())

	# the implementations for TreeModel methods are prefixed with on_

	def on_get_flags(self):
		'''Returns the GtkTreeModelFlags for this particular type of model'''
		return 0 # gtk.TREE_MODEL_ITERS_PERSIST

	def on_get_n_columns(self):
		'''Returns the number of columns in the model'''
		return 3

	def on_get_column_type(self, index):
		'''Returns the type of a column in the model'''
		return gobject.TYPE_STRING

	def on_get_path(self, node):
		'''Returns the tree path(a tuple of indices at the various
		levels) for a particular node.'''
		return node.path

	def on_get_iter(self, path):
		'''Returns the node corresponding to the given path.  In our
		case, the node is the path'''
		assert path[0] == 0
		node = self.top
		for n in path[1:]:
			node = node.nth_child(n)
		return node

	def on_get_value(self, node, column):
		'''Returns the value stored in a particular column for the node.'''
		term = node.term()
		if column == 0:
			if aterm.types.isInt(term):
				return str(term.value)
			elif aterm.types.isReal(term):
				return str(term.value)
			elif aterm.types.isStr(term):
				return repr(term.value)
			elif aterm.types.isNil(term):
				return '[]'
			elif aterm.types.isCons(term):
				return '[...]'
			elif aterm.types.isAppl(term):
				return term.name
			else:
				return '?'
		elif column == 1:
			if  aterm.types.isInt(term):
				return 'INT'
			elif aterm.types.isReal(term):
				return 'REAL'
			elif aterm.types.isStr(term):
				return 'STR'
			elif aterm.types.isList(term):
				return 'LIST'
			elif aterm.types.isAppl(term):
				return 'APPL'
			else:
				return '?'
		elif column == 2:
			if aterm.types.isAppl(term) and term.annotations:
				return ', '.join([str(anno) for anno in term.annotations])
		else:
			return None

	def on_iter_next(self, node):
		'''Returns the next node at this level of the tree'''
		return node.next()

	def on_iter_children(self, node):
		'''Returns the first child of this node'''
		return node.children()

	def on_iter_has_child(self, node):
		'''Returns true if this node has children'''
		return node.has_child()

	def on_iter_n_children(self, node):
		'''Returns the number of children of this node'''
		if node is None:
			return 1
		else:
			return node.n_children()

	def on_iter_nth_child(self, node, n):
		'''Returns the nth child of this node'''
		if node is None:
			assert n == 0
			return self.top
		else:
			return node.nth_child(n)

	def on_iter_parent(self, node):
		'''Returns the parent of this node'''
		return node.parent()


class TermWindow(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self)

		self.set_title('Term Inspector')
		self.set_default_size(500, 500)

		scrolled_window = gtk.ScrolledWindow()
		self.add(scrolled_window)
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

		self.treeview = treeview = gtk.TreeView()
		scrolled_window.add(self.treeview)
		treeview.set_enable_search(False)
		treeview.set_fixed_height_mode(True)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Term", renderer, text=0)
		column.set_resizable(True)
		column.set_fixed_width(300)
		column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Type", renderer, text=1)
		column.set_fixed_width(50)
		column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Annotations", renderer, text=2)
		column.set_resizable(True)
		column.set_fixed_width(150)
		column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		treeview.append_column(column)

		self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

		self.show_all()

	def set_term(self, term):
		treeview = self.treeview
		treemodel = TermTreeModel(term)
		treeview.set_model(treemodel)
		treeview.expand_all()

	def get_path(self, path):
		if path is not None:
			path = [int(i) for i in path]
			path.reverse()
			path = tuple([0] + path)
			return path
		else:
			return None



class TermView(TermWindow, view.View):

	def __init__(self, model):
		TermWindow.__init__(self)
		view.View.__init__(self, model)

		model.connect('notify::term', self.on_term_update)
		model.connect('notify::selection', self.on_selection_update)

		self.connect('destroy', self.on_window_destroy)

		if model.get_term() is not None:
			self.on_term_update(model.term)
		if model.get_selection() is not None:
			self.on_selection_update(model.selection)

	def get_name(self, name):
		return 'Inspector View'

	def on_term_update(self, term):
		self.set_term(term)

	def on_selection_update(self, selection):
		start, end = selection

		start = self.get_path(start)
		end = self.get_path(end)

		if start is not None and end is not None:
			tree_selection = self.treeview.get_selection()
			tree_selection.unselect_all()
			tree_selection.select_range(start, end)
			self.treeview.scroll_to_cell(start)
			#self.treeview.set_cursor(start)

	def on_window_destroy(self, event):
		model = self.model
		model.disconnect('notify::term', self.on_term_update)
		model.disconnect('notify::selection', self.on_selection_update)


class TermViewFactory(view.ViewFactory):

	def get_name(self):
		return 'Term'

	def can_create(self, model):
		return True

	def create(self, model):
		return TermView(model)


if __name__ == '__main__':
	view.main(TermView)

