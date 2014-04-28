
callviz
=======

* Python module to visualize a recursion as a tree with arguments and return values at each node. 
* Provides a decorator to instrument target functions (as opposed to trace or debugger based approaches)  
* Uses pygraphviz to render the graph. 

##usage

1. Use the @viz decorator to instrument the recursive function.

> @viz

> def factorial(n):

2. Render the recursion with 

> callgraph.render("outfile.png") 

The output file type is derived from the file name. Supported types include .dot (graphviz dot file), .png (png image), .svg (vector graphic)

##example

```python
from callviz import callgraph, viz

@viz
def quicksort(items):
    if len(items) <= 1: 
        return items
    else:
        pivot = items[0]
        lesser = quicksort([x for x in items[1:] if x < pivot])
        greater = quicksort([x for x in items[1:] if x >= pivot])
        return lesser + [pivot] + greater

print quicksort( list("helloworld") )
callgraph.render("sort.png")
```

## output 
![quicksort callviz output](http://s12.postimg.org/5f3eonikd/sort.png)


Note:
1. The edges are numbered by the order in which they were traversed by the execution.
2. The edges are colored from black to grey to indicate order of traversal : black edges first, grey edges last.

## dependencies

This requires graphviz and pygraphviz to work.


