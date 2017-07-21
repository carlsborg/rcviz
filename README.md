# rcviz

`rcviz` is a Python module to visualize recursion as a tree with arguments and return values at each node.

Features:

* Provides a decorator to instrument target functions (as opposed to trace or debugger based approaches)
* Uses Python module `graphviz`, provided by the `graphviz` software package.
* Supports IPython, particular inline viewing in Jupyter Notebooks
* Python 2 and Python 3 compatibility

## Usage
1. Create an instance of the `CallGraph` class:

	```python
	    cg = CallGraph(filename="factorial.pdf")
	```
		    
	The keyword argument `filename` is optional, and overrides the default filename. The default output  
	filename for the callgraph is `callgraph.png`, but in the above example, we override it to
	`factorial.pdf`.  The output file format is determined from the file extension provided in the filename 
	(e.g. `.pdf`). If rendered inline inside a Jupyter (IPython) Notebook, the filename parameter is  
	ignored.

2. Use the `@viz(cg)` decorator to instrument the recursive function.
    The decorator takes one required positional argument an instance of the `CallGraph` class, e.g. `cg`.

    ```python
        @viz(cg)
        def factorial(n)
            ...
    ```
3. Render the recursion callgraph through an instance of a `CallGraph` class.
    Given the above example, such as `cg` in the above example. To render a graph to a file,
    call: `cg.render()`. If called within a Jupyter Notebook cell, the filename
    parameter (whether default or overridden) is ignored.

    The output file type is derived from the file name. Supported types include .dot (graphviz dot file), .png (png image), .svg (vector graphic)

    ### Example
    ```python
    from rcviz import CallGraph, viz

    cg = CallGraph(filename="sort.pdf")

    @viz(cg)
    def quicksort(items):
        if len(items) <= 1:
            return items
        else:
            pivot = items[0]
            lesser = quicksort([x for x in items[1:] if x < pivot])
            greater = quicksort([x for x in items[1:] if x >= pivot])
            return lesser + [pivot] + greater

    print(quicksort(list("helloworld")))
    cg.render()
    ```

    **Note:** If executed inside a Jupyter Notebook cell, either `cg.render()` or `cg` will
    produce an inline callgraph, using IPython's `_repr_svg_` method protocol.


## Output
![quicksort rcviz output](http://s30.postimg.org/7chmr6q35/sort.png)

Note:

1. The edges are numbered by the order in which they were traversed by the execution.

2. The edges are colored from black to grey to indicate order of traversal : black edges first, grey edges last.

## Experimental

Show intermediate values of local variables in the output render by invoking decoratedfunction.track(param1=val1, param2=val2,...). In the quicksort example above you can track the pivot with:

```python
	pivot = items[0]
	quicksort.track(the_pivot=pivot) # shows a new row labelled the_pivot in each node 
```

## Dependencies

This requires graphviz built with Python bindings to work.

On macOS, using Homebrew:

```$ brew install --with-bindings graphviz```

On Ubuntu: 

```
# sudo apt-get install graphviz libgv-python
```

Tested on Python 2.7.3 and 3.6.1


* Setup script by [adampetrovic](https://github.com/adampetrovic).
* Python 3 compatibility added by [damnedfacts](https://github.com/damnedfacts).
