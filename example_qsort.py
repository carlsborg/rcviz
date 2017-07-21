from __future__ import print_function

from rcviz import CallGraph, viz

cg = CallGraph()
@viz(filename="sort.pdf", callgraph=cg)
def quicksort(items):
    if len(items) <= 1:
        return items
    else:
        pivot = items[0]
        quicksort.track(the_pivot=pivot) # shows a new row labelled the_pivot in each node 
        lesser = quicksort([x for x in items[1:] if x < pivot])
        greater = quicksort([x for x in items[1:] if x >= pivot])
        return lesser + [pivot] + greater
print(quicksort(list("helloworld")))

cg.render()
