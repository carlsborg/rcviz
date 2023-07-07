from typing import Dict
import pygraphviz as gviz
from .node_data import node_data


def render(digraph_data: Dict[int, node_data], counter: int, filename: str):
    g = gviz.AGraph(strict=False, directed=True)
    g.graph_attr["label"] = f"rcviz nodes={len(digraph_data)}"
    g.graph_attr["fontcolor"] = "gray"

    # create nodes
    for frame_id, node in digraph_data.items():
        auxstr = ""
        for param, val in node.auxdata.items():
            aug_data_row = f"<tr><td>{param}:{val}</td></tr>"
            auxstr += aug_data_row
        label = f'<<table border="0" bgcolor="#eeeeee" color="gray" rows="*" style="rounded"> <tr><td>{node.fn_name}({node.argstr()})</td></tr>{auxstr}<tr><td>ret: {node.ret}</td></tr></table>>'
        g.add_node(
            str(frame_id), shape="plain", label=label, fontsize=13, labelfontsize=13
        )

    # edge colors
    step = 200 / counter
    cur_color = 0

    # create edges
    for frame_id, node in digraph_data.items():
        child_nodes = []
        for child_id, counter, unwind_counter in node.child_methods:
            child_nodes.append(child_id)
            cur_color = step * counter
            color = "#%2x%2x%2x" % (int(cur_color), int(cur_color), int(cur_color))
            label = "%s (&uArr;%s)" % (counter, unwind_counter)
            g.add_edge(
                str(frame_id),
                str(child_id),
                label=label,
                color=color,
                fontsize=8,
                labelfontsize=8,
                fontcolor="#999999",
            )

        # order edges l to r
        if len(child_nodes) > 1:
            sg = g.add_subgraph(child_nodes, rank="same")
            prev_node_id = None
            for child_node_id in child_nodes:
                if prev_node_id:
                    sg.add_edge(str(prev_node_id), str(child_node_id), style="invis")
                prev_node_id = child_node_id

    g.layout()

    if filename:
        g.draw(path=filename, prog="dot")
        print("callviz: rendered to %s" % filename)
    else:
        #If path is None, the result is returned as a Bytes object
        return g.draw(path=None, prog="dot", format="png")

