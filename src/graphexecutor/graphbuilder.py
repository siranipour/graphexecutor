import inspect

import matplotlib.pyplot as plt
import networkx as nx

from graphexecutor import graphchecker as gc

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


def find_node_dependencies(node, spec_func_map):
    if isinstance(node, LeafNode):
        return None

    func = node.func
    sig = inspect.signature(func)
    deps = sig.parameters.keys()
    spec_dependencies = []
    for dep in deps:
        if dep in spec_func_map:
            func = spec_func_map[dep]
            node_dependency = FunctionNode(func)
        else:
            node_dependency = LeafNode(dep)
        spec_dependencies.append(node_dependency)

    return spec_dependencies


def connect_node_to_dependencies(graph, node, spec_func_map): # The graph here is like a global object
                                               # think of passing it by reference in C++
    """Connect a given node with all
    its dependencies
    """
    deps = find_node_dependencies(node, spec_func_map)
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


def _solution_getter(**kwargs):
    return kwargs


# Connects any disjoint graphs and holds all the requested solutions in one node
def add_solution_node(graph, base_nodes):

    solution_node = FunctionNode(_solution_getter)
    solution_node.final_action = True

    for base_node in base_nodes:
        graph.add_edge(solution_node, base_node)

    return graph


def complete_graph(graph, spec_func_map):
    """Find all nodes that need wiring and wire them
    """
    to_wire = nodes_to_wire(graph)
    if not to_wire:
        return graph

    for node in to_wire:
        graph = connect_node_to_dependencies(graph, node, spec_func_map)
    return complete_graph(graph, spec_func_map)


def actions_to_graph(base_nodes, spec_func_map):
    base_graph = create_base_graph(base_nodes)
    completed_graph = complete_graph(base_graph, spec_func_map)
    graph_with_solution_node = add_solution_node(completed_graph, base_nodes)
    gc.check_for_cycles(graph_with_solution_node)
    return graph_with_solution_node


def graph_leaves(graph):
    # The inputs
    f = lambda node: isinstance(node, LeafNode)
    return list(filter(f, graph.nodes))


def find_solution_node(graph):
    for node in graph.nodes:
        if getattr(node, 'final_action', False):
            return node
    return None


def visualize_graph(graph):
    from networkx.drawing.nx_agraph import graphviz_layout
    fig, ax = plt.subplots()
    graph = nx.reverse(graph, copy=True)
    pos = graphviz_layout(graph, prog='dot')
    nx.draw(graph, pos, with_labels=True, arrows=True)
    return fig