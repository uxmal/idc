'''Box viewing.'''


import gtk
import pango

import box
import ir.pprint

from ui.menus import PopupMenu


class Range:

	def __init__(self, path, start, end = None):
		self.path = path
		self.start = start
		self.end = end
		self.subranges = []

	def __cmp__(self, other):
		return cmp(self.start, other.start)

	def contains(self, set):
		return self.start <= set <= self.end

	def contains_range(self, start, endiff):
		return self.contains(start) and self.contains(end)

	def get_path_at_offset(self, offset):
		if not self.contains(offset):
			return None
		for subrange in self.subranges:
			path = subrange.get_path_at_offset(offset)
			if path is not None:
				return path
		return self.path

	def get_range_at_path(self, path):
		# TODO: use a hash table
		if self.path == path:
			return self.start, self.end
		for subrange in self.subranges:
			result = subrange.get_range_at_path(path)
			if result is not None:
				return result
		return None


class TextBufferFormatter(box.Formatter):
	'''Formats into a TextBuffer.'''

	# See hypertext.py example included in pygtk distribution

	def __init__(self, buffer):
		box.Formatter.__init__(self)

		self.buffer = buffer

		self.buffer.set_text("", 0)
		self.iter = self.buffer.get_iter_at_offset(0)

		self.types = {}
		self.types['operator'] = self.buffer.create_tag(None,
			foreground = 'black'
		)
		self.types['keyword'] = self.buffer.create_tag(None,
			foreground = 'black',
			weight=pango.WEIGHT_BOLD
		)
		self.types['literal'] = self.buffer.create_tag(None,
			foreground = 'dark blue',
			#foreground = 'green',
			#style=pango.STYLE_ITALIC,
		)
		self.types['symbol'] = self.buffer.create_tag(None,
			foreground = 'dark blue',
			style=pango.STYLE_ITALIC,
		)

		self.default_highlight_tag = self.buffer.create_tag(None)
		self.highlight_tag_stack = [self.default_highlight_tag]

		default_path_tag = self.buffer.create_tag(None)
		self.range_stack = []

	def write(self, s):
		highlight_tag = self.highlight_tag_stack[-1]
		self.buffer.insert_with_tags(self.iter, s, highlight_tag)

	def handle_tag_start(self, name, value):
		if name == 'type':
			highlight_tag = self.types.get(value, self.default_highlight_tag)
			self.highlight_tag_stack.append(highlight_tag)
		if name == 'path':
			range = Range(value, self.get_offset())
			self.range_stack.append(range)

	def handle_tag_end(self, name):
		if name == 'type':
			self.highlight_tag_stack.pop()
		if name == 'path':
			assert self.range_stack
			range = self.range_stack.pop()
			assert range.end is None
			range.end = self.get_offset()
			if self.range_stack:
				self.range_stack[-1].subranges.append(range)
			else:
				self.buffer.range = range
			self.buffer.path_range[range.path] = range.start, range.end

	def get_offset(self):
		# TODO: keep track of offset
		return self.buffer.get_iter_at_mark(self.buffer.get_insert()).get_offset()


class BoxBuffer(gtk.TextBuffer):

	def __init__(self, model):
		gtk.TextBuffer.__init__(self, None)
		self.model = model
		self.range = None
		self.path_range = {}
		model.connect('notify::term', self.on_term_update)
		model.connect('notify::selection', self.on_selection_update)

	def on_term_update(self, term):
		boxes = ir.pprint.module(term)
		self.set_text("")
		self.range = None
		self.path_range = {}
		formatter = TextBufferFormatter(self)
		box.write(boxes, formatter)
		self.place_cursor(self.get_start_iter())

	def on_selection_update(self, selection):
		start, end = selection
		if start or end:
			# TODO: this is often unnecessary
			try:
				start, dummy = self.get_iters_at_path(start)
				dummy, end = self.get_iters_at_path(end)
			except Exception, ex:
				print ex
				return
		else:
			start = end = self.get_start_iter()
		self.select_range(start, end)

	def get_path_at_iter(self, iter):
		if self.range is None:
			return None
		off = iter.get_offset()
		path = self.range.get_path_at_offset(off)
		return path

	def get_iters_at_path(self, path):
		try:
			start, end = self.path_range[path]
		except KeyError:
			return None
		start = self.get_iter_at_offset(start)
		end = self.get_iter_at_offset(end)
		return start, end


class BoxView(gtk.TextView):

	def __init__(self, model):
		gtk.TextView.__init__(self, BoxBuffer(model))
		self.model = model
		self.set_editable(False)
		self.connect("event", self.on_button_press)

	def on_button_press(self, textview, event):
		'''Update the selection paths.'''

		buffer = textview.get_buffer()

		start = buffer.get_iter_at_mark(buffer.get_selection_bound())
		end = buffer.get_iter_at_mark(buffer.get_insert())

		if event.type == gtk.gdk.BUTTON_RELEASE and event.button == 1:
			start = buffer.get_path_at_iter(start)
			end = buffer.get_path_at_iter(end)
			self.model.set_selection((start, end))
			return False

		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
			x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
			iter = textview.get_iter_at_location(x, y)
			#print start.get_offset(), end.get_offset()
			if iter.in_range(start, end):
				# user clicked inside the selected range
				start = buffer.get_path_at_iter(start)
				end = buffer.get_path_at_iter(end)
			else:
				# user clicked outside the selected range
				path = buffer.get_path_at_iter(iter)
				self.model.set_selection((path, path))

			popupmenu = PopupMenu(self.model)
			popupmenu.popup( None, None, None, event.button, event.time)
			return True

		return False


