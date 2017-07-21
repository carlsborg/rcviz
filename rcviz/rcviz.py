# rcviz : a small recursion call graph vizualization decorator
# Copyright (c) Ran Dugal 2014
# Licensed under the GPLv2, which is available at
# http://www.gnu.org/licenses/gpl-2.0.html

from __future__ import print_function

import inspect
import logging
import copy
import os
from pathlib import Path
import graphviz as gviz
import __main__

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

try:
    __IPYTHON__ = get_ipython()
    import ipykernel.zmqshell
    import IPython.terminal.interactiveshell
    #if float(gviz.__version__[0:3]) < 1.4:
    #    raise RuntimeError("IPython used with pygraphviz < 1.4 will experience "
    #                       "some bugs")
    #from IPython.display import Image
except NameError:
    __IPYTHON__ = None

try:
    __main__file__ = inspect.getfile(__main__)
except TypeError:
    if __IPYTHON__:
        __main__file__ = "<ipython-input-"


def trim_stack(stack):
    if __IPYTHON__:
        for i in range(len(stack) - 1, -1, -1):
            if os.path.basename(stack[i].filename).startswith(__main__file__):
                break
        return stack[:i+1]
    else:
        return stack

class CallGraph(object):
    '''singleton class that stores global graph data
       draw graph using pygraphviz
    '''
    def __init__(self, filename="callgraph.png"):
        self._callers = {} # caller_fn_id : NodeData
        self._counter = 1  # track call order
        self._unwindcounter = 1 # track unwind order
        self._frames = [] # keep frame objects reference
        self.graph = None
        self.filename = filename

    def reset(self):
        self.__init__()

    def get_callers(self):
        return self._callers

    def get_counter(self):
        return self._counter

    def get_unwindcounter(self):
        return self._unwindcounter

    def increment(self):
        self._counter += 1

    def increment_unwind(self):
        self._unwindcounter += 1

    def get_frames(self):
        return self._frames

    def render(self, show_null_returns=True):
        if self.graph:
            self.reset()

        filename = self.filename
        p = Path(filename)
        ext = p.suffix[1:] if p.suffix else "png"
        filename = filename[:-len(ext)-1] if p.suffix else filename

        g = gviz.Digraph(format=ext)
        g.graph_attr['label'] = 'nodes=%s' % len(self._callers)
        g.graph_attr['fontname'] = "helvetica"
        g.node_attr['fontname'] = "helvetica"
        g.edge_attr['fontname'] = "helvetica"

        # create nodes
        for frame_id, node in self._callers.items():

            auxstr = ""
            for param, val in node.auxdata.items():
                auxstr += " | %s: %s" % (param, val)

            if not show_null_returns and node.ret is None:
                label = "{ %s(%s) %s }" % (node.fn_name, node.argstr(), auxstr)
            else:
                label = "{ %s(%s) %s | ret: %s }" % (node.fn_name,
                                                     node.argstr(),
                                                     auxstr, node.ret)
            g.node(str(frame_id), shape='Mrecord', label=label,
                   fontsize=str(13), labelfontsize=str(13))

        # edge colors
        step = 200 // self._counter
        cur_color = 0

        # create edges
        for frame_id, node in self._callers.items():
            child_nodes = []
            for child_id, counter, unwind_counter in node.child_methods:
                child_nodes.append(child_id)
                cur_color = step * counter
                color = "#%2x%2x%2x" % (cur_color, cur_color, cur_color)
                label = "%s (&uArr;%s)" % (counter, unwind_counter)
                g.edge(str(frame_id), str(child_id), label=label, fontcolor="#999999",
                       color=str(color), fontsize=str(8), labelfontsize=str(8))

            # order edges l to r
            # FIXME: This code doesn't seem to do anything
            # It causes the Graphviz dot command to issue 
            # compilation errors (it affects Jupyter's display due to the
            # non-zero return value).
            """if len(child_nodes) > 1:
                sg = gviz.Digraph(name="foo")
                sg.graph_attr['rank'] = 'same'
                prev_node = None
                for child_node in child_nodes:
                    if prev_node:
                        sg.edge(str(prev_node), str(child_node),
                                color="#ffffff")
                    prev_node = child_node
                g.subgraph(sg)"""

        self.graph = g
        if not __IPYTHON__ or isinstance(__IPYTHON__, IPython.terminal.interactiveshell.TerminalInteractiveShell):
            print("callviz: rendered to %s" % (self.filename))
            g.render(filename=filename)
        elif isinstance(__IPYTHON__, ipykernel.zmqshell.ZMQInteractiveShell):
            print("callviz: Rendering in inline in Jupyter Notebook")
            return g

    def _repr_svg_(self):
        svg = self.render()._repr_svg_()
        self.reset()
        return svg

class NodeData(object):
    def __init__(self, _args=None, _kwargs=None, _fnname="",
                 _ret=None, _childmethods=[]):
        self.args = _args
        self.kwargs = _kwargs
        self.fn_name = _fnname
        self.ret = _ret
        self.child_methods = _childmethods    # [ (method, gcounter) ]

        self.auxdata = {} # user assigned track data

    def __str__(self):
        return "%s -> child_methods: %s" % (self.nodestr(), self.child_methods)

    def nodestr(self):
        return "%s = %s(%s)" % (self.ret, self.fn_name, self.argstr())

    def argstr(self):
        s_args = ",".join([str(arg) for arg in self.args])
        s_kwargs = ",".join([(str(k), str(v)) 
                             for (k, v) in self.kwargs.items()])
        return "%s%s" % (s_args, s_kwargs)

class viz(object):
    """decorator to construct the call graph with args
       and return values as labels
    """

    def __init__(self, callgraph, *args, **kwargs):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self._verbose = False
        if not isinstance(callgraph, CallGraph):
            raise ValueError("@viz decorator must be called with a CallGraph instance")
        self.callgraph = callgraph

    def track(self, **kwargs):
        fullstack = trim_stack(inspect.stack())
        call_frame_id = id(fullstack[2][0])
        g_callers = self.callgraph.get_callers()
        node = g_callers.get(call_frame_id)
        if node:
            node.auxdata.update(copy.deepcopy(kwargs))

    def __call__(self, f, *args, **kwargs):
        """
        With decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """

        def wrapped_f(*args, **kwargs):
            # Expected parameters for the function being wrapped
            g_callers = self.callgraph.get_callers()
            g_frames = self.callgraph.get_frames()

            # find the caller frame, and add self as a child node
            caller_frame_id = None

            fullstack = trim_stack(inspect.stack())

            if self._verbose:
                logging.debug("Full Stack:")
                for stack in fullstack:
                    logging.debug("\t" + str(stack))

            if len(fullstack) > 2:
                caller_frame_id = id(fullstack[2][0])

                if self._verbose:
                    logging.debug("Caller Frame: %s %s" % (caller_frame_id,
                                                           fullstack[2]))

            this_frame_id = id(fullstack[0][0])
            if self._verbose:
                logging.info("This Frame: %s %s" % (this_frame_id, fullstack[0]))

            if this_frame_id not in g_frames:
                g_frames.append(fullstack[0][0])

            if this_frame_id not in g_callers.keys():
                g_callers[this_frame_id] = NodeData(args, kwargs,
                                                    f.__name__,
                                                    None, [])

            edgeinfo = None
            if caller_frame_id:
                edgeinfo = [this_frame_id, self.callgraph.get_counter()]
                g_callers[caller_frame_id].child_methods.append(edgeinfo)
                self.callgraph.increment()


            ret = f(*args, **kwargs)
            g_callers[this_frame_id].ret = copy.deepcopy(ret)

            if self._verbose:
                logging.debug('Unwinding Frame ID: %s' % this_frame_id)

            if edgeinfo:
                edgeinfo.append(self.callgraph.get_unwindcounter())
                self.callgraph.increment_unwind()

            return ret

        wrapped_f.track = self.track
        return wrapped_f
