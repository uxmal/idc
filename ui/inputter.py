'''Refactoring user input abstraction.'''


import gtk

import transf.lib.ui


class Inputter(transf.lib.ui.Inputter):
	'''GTK-based user data inputter.'''

	def inputStr(self, title, text):
		parent = None
		dialog = gtk.Dialog(
			title,
			parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
			gtk.STOCK_OK, gtk.RESPONSE_OK)
		)
		dialog.set_default_response(gtk.RESPONSE_OK)

		textlabel = gtk.Label(text)
		dialog.vbox.pack_start(textlabel)

		textentry = gtk.Entry()
		textentry.set_activates_default(True)
		dialog.vbox.add(textentry)

		dialog.show_all()

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			result = textentry.get_text()
		else:
			result = None

		dialog.destroy()
		return result


# override default text inputter
transf.lib.ui.inputter = Inputter()


if __name__ == '__main__':
	inputter = Inputter()
	print inputter.inputStr("Title", "Question?")
