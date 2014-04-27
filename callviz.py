import inspect
import pygraphviz as gviz
import logging

class callgraph(object):
	'''singleton class that stores global graph data 
	   draw graph using pygraphviz
	'''

	_callers = {} # caller_fn_id : node_data
	_counter = 1
	_frames = [] # keep frame objects reference

	@staticmethod
	def reset():
		callgraph._callers = {}
		callgraph._counter = 1
		callgraph._frames = []
		
	@staticmethod
	def get_callers():
		return callgraph._callers

	@staticmethod
	def get_counter():
		return callgraph._counter

	@staticmethod
	def increment():
		callgraph._counter += 1

	@staticmethod
	def get_frames():
		return callgraph._frames

	@staticmethod		
	def render(filename):

		if not filename: 
			filename = "out.svg"

		g = gviz.AGraph(strict=False, directed=True)
		g.graph_attr['label']='nodes=%s' % len(callgraph._callers)

		# create nodes
		for frame_id, node in callgraph._callers.iteritems():
			g.add_node( frame_id, shape='Mrecord', label= "{ %s(%s) | ret: %s }" % (node.fn_name, node.argstr(), node.ret), fontsize=13, labelfontsize=13)

		# edge colors
		step = 200 / callgraph._counter
		cur_color = 0

		# create edges
		for frame_id, node in callgraph._callers.iteritems():
			for (child_id, counter) in node.child_methods:
				cur_color = step * counter
				color = "#%2x%2x%2x" % (cur_color, cur_color, cur_color )
				g.add_edge( frame_id, child_id, label=str(counter), color= color, fontsize=8, labelfontsize=8, fontcolor="#999999" )
			logging.info( "%s, %s" % (frame_id, node) ) 

		g.layout()

		g.draw(path=filename, prog='dot')

		print "callviz: rendered to %s" % filename

class node_data(object):

	def __init__(self, _args=None, _kwargs=None, _fnname="", _ret=None, _childmethods=[]):
		self.args  	= _args 
		self.kwargs = _kwargs
		self.fn_name = _fnname
		self.ret	= _ret
		self.child_methods = _childmethods	# [ (method, gcounter) ]

	def __str__(self):
		return "%s -> child_methods: %s" % (self.nodestr(), self.child_methods)

	def nodestr(self):
		return "%s = %s(%s)" % (self.ret, self.fn_name, self.argstr())

	def argstr(self):
		s_args =  ",".join( [str(arg) for arg in self.args] )
		s_kwargs = ",".join( [(str(k), str(v)) for (k,v) in self.kwargs.items()] )
		return "%s%s" % (s_args, s_kwargs)

class viz(object):
	''' decorator to construct the call graph with args and return values as labels '''

	def __init__(self, wrapped):
		self._verbose = False
		self.wrapped = wrapped
		print "initing ", id(self)

	def __call__(self, *args, **kwargs):

		g_callers = callgraph.get_callers()
		g_frames  = callgraph.get_frames()

		# find the caller frame, and add self as a child node
		caller_frame_id = None

		fullstack = inspect.stack()

		if (self._verbose):
			logging.debug("full stack: %s" % str(fullstack))

		if len (fullstack) > 2:
			caller_frame_id = id(fullstack[2][0])
			if ( self._verbose ):
				logging.debug("caller frame: %s %s" % (caller_frame_id, fullstack[2]))

		this_frame_id = id(fullstack[0][0])
		if (self._verbose):
			logging.info("this frame: %s %s" % (this_frame_id, fullstack[0]))

		if this_frame_id not in g_frames:
			g_frames.append( fullstack[0][0] )

		if  this_frame_id not in g_callers.keys():
			g_callers[this_frame_id] = node_data(args, kwargs, self.wrapped.__name__, None, [])

		if caller_frame_id:
			g_callers[caller_frame_id].child_methods.append((this_frame_id, callgraph.get_counter()))
			callgraph.increment()

		ret = self.wrapped(*args, **kwargs)

		if (self._verbose):
			logging.debug('unwinding frame id: %s' % this_frame_id)

		g_callers[this_frame_id].ret = ret

		return ret

