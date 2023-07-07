from rcviz import callgraph, viz


@viz
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(4)

callgraph.render("fibonacci.svg")

