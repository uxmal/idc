'''Dot pretty-printing.'''


from transf import parse
import box


parse.Transfs('''

ppId = strings.tostr

ppAttr =
		Attr(name, value)
			-> H([ <ppId name>, "=", <ppId value> ])

ppAttrs =
		!H([ "[", <Map(ppAttr); box.commas>, "]" ])

ppNode =
		Node(nid, attrs, _)
			-> H([ <ppId nid>, <ppAttrs attrs> ])

ppNodes = lists.Map(ppNode)

ppNodeEdge =
		Edge(dst, attrs)
			-> H([ <ppId src>, "->", <ppId dst>, <ppAttrs attrs> ])

ppNodeEdges =
		Node(src, _, edges)
			-> <Map(ppNodeEdge) edges>

ppEdges =
	lists.MapConcat(ppNodeEdges)

ppGraph =
		Graph(nodes)
			-> V([
				H([ "digraph", " ", "{" ]),
				V( <ppNodes nodes> ),
				V( <ppEdges nodes> ),
				H([ "}" ])
			])

pprint = ppGraph

''')
