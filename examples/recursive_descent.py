# Example recursive descent parser from Prof. Tim Finin 
# https://github.com/finin/recursive_descent

from rcviz import callgraph, viz
import sys

# some special characters
PARENS = ['(', ')']
ADD_OPS = ['+', '-']
MUL_OPS = ['*', '/']
OPS = ADD_OPS + MUL_OPS

@viz
def parse(string):
    """ Returns tuple representing parse tree for string or None if
    grammar doesn't accept string"""
    tree, rest = parse_exp(tokenize(string))
    if not tree:
        print('syntax error at "%s"' % ' '.join(rest))
        return None
    elif rest:
        print('syntax error: found %s but "%s" remains' % (tree, ' '.join(rest)))
        return None
    else:
        return tree

@viz
def parse_exp(tokens):
    """ Looks for an EXP in the token stream, returning (T,R) if one
    is found where T is the EXP tree and R is a list of remaining
    tokens. Returns (None, tokens) if no EXP can be parsed"""
    tree,rest = parse_term(tokens)
    if not tree:
        return fail(tokens)
    elif rest and rest[0] in ADD_OPS:
        tree2, rest2 = parse_exp(rest[1:])
        if tree2:
            return ((rest[0], tree, tree2), rest2)
        else:
            return fail(rest2)
    else:
        return (tree, rest)

@viz
def parse_term(tokens):
    """ Looks for an TERM in the token stream, returning (T,R) if one
    is found where T is the TERM's tree and R is a list of remaining
    tokens. Returns (None, tokens) if no TERM can be parsed"""    
    tree, rest = parse_factor(tokens)
    if not tree:
        return fail(tokens)
    elif not rest:
        return (tree, rest)
    elif rest[0] in MUL_OPS:
        tree2, rest2 = parse_term(rest[1:])
        if tree2:
            return ((rest[0], tree, tree2), rest2)
        else:
            return fail(rest)
    return (tree, rest)

@viz
def parse_factor(tokens):
    """ Looks for an FACTOR in the token stream, returning (T,R) if one
    is found where T is the FACTOR's tree and R is a list of remaining
    tokens. Returns (None, tokens) if no FACTOR can be parsed"""
    if tokens[0] == '(':
        tree,rest = parse_exp(tokens[1:])
        if not tree: return fail(tokens)
        if rest[0] != ')': return fail(rest)
        return (tree, rest[1:])
    else:
        return parse_num(tokens)
@viz
def parse_num(tokens):
    """ Looks for an NUM returning (N,R) if found where N is number or
    None (if number can't be parsed) and R a list of remaining tokens"""
    n = num(tokens[0])
    return (n, tokens[1:] if n else tokens)

@viz
def fail(tokens):
    return (None, tokens)

@viz
def tokenize(s):
    """ Return list of tokens in the string.  Wraps spaces around
    operators and splits on whitespace"""
    for x in OPS + PARENS:
        s = s.replace(x, ' ' + x + ' ')
    return s.split()

@viz    
def num (s):
    """ Return int or float from s or returns None"""
    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            return None

if __name__ == "__main__":
    print(parse(("2+3*(4+5)")))
    callgraph.render("parse.png")

