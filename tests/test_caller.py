import logging
from rcviz import callgraph, viz


@viz
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)


def test_caller():
    logging.getLogger().setLevel(logging.DEBUG)
    fib(4)

    # callgraph.render("fib.png")
    digraph_data, wind_counter = callgraph.digraph_data()

    assert wind_counter == 9 
    assert len(digraph_data) == 9
    assert all([node.fn_name == "fib" for node in digraph_data.values()])

    sum_edges = 0 
    for _, node in digraph_data.items():
        sum_edges += len(node.child_methods)
    assert sum_edges == 8


if __name__ == "__main__":
    test_caller()

