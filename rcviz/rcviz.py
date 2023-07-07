# rcviz : a small recursion call graph vizualization decorator
# Copyright (c) Ran Dugal 2014
# Licensed under the GPLv2, which is available at
# http://www.gnu.org/licenses/gpl-2.0.html

import copy
import inspect
from typing import List
from os import getenv

from .callgraph import callgraph
from .node_data import node_data


class viz(object):
    """decorator to construct the call graph with args and return values as labels"""

    def __init__(self, wrapped):
        self._verbose = getenv("RCVIZ_VERBOSE", False)
        self.wrapped = wrapped

    def track(self, **kwargs):
        call_frame_id = id(inspect.stack()[2][0])
        g_callers = callgraph.get_callers()
        node = g_callers.get(call_frame_id)
        if node:
            node.auxdata.update(copy.deepcopy(kwargs))

    def _print_stack(self, fullstack: List[inspect.FrameInfo], caller_frame_id):
        print(f"\n\nouter stack #{callgraph.get_counter()}")
        for frame_info in fullstack:
            print(
                f"\t{id(frame_info.frame)} {frame_info.filename}:{frame_info.lineno} {str(frame_info.function)}"
            )
        print(f"caller: {caller_frame_id}")

    def __call__(self, *args, **kwargs):
        g_callers = callgraph.get_callers()
        g_frames = callgraph.get_frames()

        # find the caller frame, and add self as a child node
        caller_frame_id = None

        fullstack = inspect.stack()
        if len(fullstack) > 2:
            caller_frame_id = id(fullstack[2][0])
        this_frame_id = id(fullstack[0][0])

        if self._verbose:
            self._print_stack(fullstack, caller_frame_id)

        if this_frame_id not in g_frames:
            g_frames.append(fullstack[0][0])

        if this_frame_id not in g_callers.keys():
            g_callers[this_frame_id] = node_data(
                args, kwargs, self.wrapped.__name__, None, []
            )

        edgeinfo = None
        if caller_frame_id and g_callers.get(caller_frame_id):
            edgeinfo = [this_frame_id, callgraph.get_counter()]
            g_callers[caller_frame_id].child_methods.append(edgeinfo)
            callgraph.increment()

        # invoke wraped
        ret = self.wrapped(*args, **kwargs)

        if self._verbose:
            print("unwinding frame id: %s" % this_frame_id)

        if edgeinfo:
            edgeinfo.append(callgraph.get_unwindcounter())
            callgraph.increment_unwind()

        g_callers[this_frame_id].ret = copy.deepcopy(ret)

        return ret

 