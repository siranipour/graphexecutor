import functools
import inspect

import matplotlib.pyplot as plt
import networkx as nx

import actions

# Like providers
FUNCTION_MAPPING = dict(inspect.getmembers(actions, inspect.isfunction))


class CycleError(Exception): pass


class Node:
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name


class FunctionNode(Node):
    def __init__(self, func):
        self.name = func.__name__
        self.func = func
    def __repr__(self):
        return f"FunctionNode({self.name})"


class LeafNode(Node):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"StaticNode({self.name})"


def find_node_dependencies(node):
    if isinstance(node, LeafNode):
        return None

    func = node.func
    sig = inspect.signature(func)
    deps = sig.parameters.keys()
    spec_dependencies = []
    for dep in deps:
        if dep in FUNCTION_MAPPING:
            func = FUNCTION_MAPPING[dep]
            node_dependency = FunctionNode(func)
        else:
            node_dependency = LeafNode(dep)
        spec_dependencies.append(node_dependency)

    return spec_dependencies


def connect_node_to_dependencies(graph, node): # The graph here is like a global object
                                               # think of passing it by reference in C++
    """Connect a given node with all
    its dependencies
    """
    deps = find_node_dependencies(node)
    for dep in deps:
        graph.add_edge(node, dep)
    return graph


def nodes_to_wire(graph):
    f = lambda node: isinstance(node, FunctionNode) and graph.out_degree(node) == 0
    return list(filter(f, graph.nodes))


def create_base_graph(base_nodes):
    graph = nx.DiGraph()
    for node in base_nodes:
        graph.add_node(node)
    return graph


def check_for_cycles(f):
    @functools.wraps(f)
    def checker(*args, **kwargs):
        graph = f(*args, **kwargs)
        cycles = list(nx.simple_cycles(graph))
        for idx, cycle in enumerate(cycles):
            cycles[idx] = [node.name for node in cycle]
        if cycles:
            raise CycleError(
                "The following cyclic dependencies exist "
                f"in the dependency graph {cycles}"
                )
        return graph
    return checker


@check_for_cycles
def complete_graph(graph):
    """Find all nodes that need wiring and wire them
    """
    to_wire = nodes_to_wire(graph)
    if not to_wire:
        return graph

    for node in to_wire:
        graph = connect_node_to_dependencies(graph, node)
    return complete_graph(graph)


def actions_to_graph(base_nodes):
    base_graph = create_base_graph(base_nodes)
    try:
        completed_graph = complete_graph(base_graph)
    except RecursionError as e:
        raise RuntimeError("Recursion limit exceeded. Possible cyclic dependency") from e
    return completed_graph


def visualize_graph(graph):
    from networkx.drawing.nx_agraph import graphviz_layout
    fig, ax = plt.subplots()
    graph = nx.reverse(graph, copy=True)
    pos = graphviz_layout(graph, prog='dot')
    nx.draw(graph, pos, with_labels=True, arrows=True)
    return fig