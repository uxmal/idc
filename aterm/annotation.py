'''High-level term annotation.'''


from aterm import types
from aterm import lists


def get(term, label):
	'''Gets an annotation associated with this label.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if not types.isAppl(term):
		return term
	def withLabel(term):
		return types.isAppl(term) and term.name == label
	if term.annotations:
		anno = lists.fetch(withLabel, term.annotations)
		if anno is not None:
			return anno
	raise ValueError("undefined annotation", label)


def set(term, anno):
	'''Returns a new version of this term with the
	annotation associated with this label added or updated.'''
	if not types.isAppl(anno):
		raise TypeError("annotation is not an application term", anno)
	if not types.isAppl(term):
		return term
	label = anno.name
	def withoutLabel(term):
		return not (types.isAppl(term) and term.name == label)
	annos = lists.filter(withoutLabel, term.annotations)
	annos = term.factory.makeCons(anno, annos)
	return term.setAnnotations(annos)


def remove(term, label):
	'''Returns a copy of this term with the
	annotation associated with this label removed.'''
	if not isinstance(label, basestring):
		raise TypeError("label is not a string", label)
	if not types.isAppl(term):
		return term
	def withoutLabel(term):
		return not (types.isAppl(term) and term.name == label)
	annos = lists.filter(withoutLabel, term.annotations)
	return term.setAnnotations(annos)

