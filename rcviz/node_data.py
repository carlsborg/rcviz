from typing import List, Tuple

class node_data(object):

    def __init__(self, _args=None, _kwargs=None, _fnname="", _ret=None, _childmethods=[]):
        self.args = _args
        self.kwargs = _kwargs
        self.fn_name = _fnname
        self.ret = _ret
        self.child_methods: List[Tuple[str, int]] = _childmethods  # [ (method, gcounter) ]

        self.auxdata = {}  # user assigned track data

    def __str__(self):
        return "%s -> child_methods: %s" % (self.nodestr(), self.child_methods)

    def nodestr(self):
        return "%s = %s(%s)" % (self.ret, self.fn_name, self.argstr())

    def argstr(self):
        s_args = ",".join([str(arg) for arg in self.args])
        s_kwargs = ",".join([(str(k), str(v))
                             for (k, v) in self.kwargs.items()])
        return "%s%s" % (s_args, s_kwargs)


