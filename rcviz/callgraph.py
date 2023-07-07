from typing import Dict, List, Optional
from .node_data import node_data
from .render_pygraphviz import render


class IpythonSVGRenderer:
    def __init__(self, svg_data):
        self._svg_data = svg_data

    def _repr_png_(self):
        return self._svg_data


def in_ipython() -> bool:
    try:
        eval("__IPYTHON__")
    except NameError:
        return False
    else:  # pragma: no cover
        return True


class callgraph(object):
    """
    singleton class that stores global graph data
    """

    _callers: Dict[int, node_data] = {}  # caller_fn_id : node_data
    _counter = 1  # track call order
    _unwindcounter = 1  # track unwind order
    _frames: List[int] = []  # keep frame objects reference

    @staticmethod
    def reset():
        callgraph._callers = {}
        callgraph._counter = 1
        callgraph._frames = []
        callgraph._unwindcounter = 1

    @staticmethod
    def get_callers():
        return callgraph._callers

    @staticmethod
    def get_counter():
        return callgraph._counter

    @staticmethod
    def get_unwindcounter():
        return callgraph._unwindcounter

    @staticmethod
    def increment():
        callgraph._counter += 1

    @staticmethod
    def increment_unwind():
        callgraph._unwindcounter += 1

    @staticmethod
    def get_frames():
        return callgraph._frames

    @staticmethod
    def digraph_data():
        return callgraph._callers, callgraph._counter

    @staticmethod
    def render(filename: Optional[str] = None):
        if not filename:
            if in_ipython():
                return IpythonSVGRenderer(
                    render(callgraph._callers, callgraph._counter, filename=None)
                )
            else:
                filename="out.svg"
        render(callgraph._callers, callgraph._counter, filename)
