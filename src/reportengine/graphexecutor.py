import actions
from graphbuilder import actions_to_graph, FunctionNode, LeafNode

from dask.delayed import delayed
import networkx as nx


def required_keys(graph):
    leaves = graph_leaves(graph)
    return [node.name for node in leaves]


def unused_keys(rootns, graph):
    leaves = set(graph_leaves(graph))
    leaf_names = {leaf.name for leaf in leaves}

    rootns_keys = set(rootns.keys())

    return set.difference(rootns_keys, leaf_names)


def graph_leaves(graph):
    # The inputs
    f = lambda node: isinstance(node, LeafNode)
    return list(filter(f, graph.nodes))


def graph_roots(graph):
    # The nodes that connect all the dependencies
    f = lambda node: graph.in_degree(node) == 0
    return list(filter(f, graph))


def to_delayed_graph(graph):
    for node in graph.nodes:
        if hasattr(node, 'func'):
            f = node.func
            node.func = delayed(f)
    return graph


def fill_leaves(graph, rootns):
    nodes_to_fill = graph_leaves(graph)
    for node in nodes_to_fill:
        new_attrs = {node: {'value': rootns[node.name], 'filled': True}}
        nx.set_node_attributes(graph, new_attrs)
    return graph


def nodes_to_evaluate_next(graph):
    nodes = set()
    filled_nodes = nx.get_node_attributes(graph, 'filled')
    for node in graph.nodes:
        # TODO: maybe remove the list cast
        successors = set(graph.successors(node))
        successors_filled = successors.issubset(filled_nodes)

        this_node_filled = node in filled_nodes
        if not this_node_filled and successors_filled:
            nodes.add(node)
    return nodes


def evaluate_node(graph, node):
    children = list(graph.successors(node))
    node_value_mapping = nx.get_node_attributes(graph, 'value')

    calling_dict = {}
    for child in children:
        calling_dict[child.name] = node_value_mapping[child]

    res = node.func(**calling_dict)

    node_res_map = {node: {'value': res, 'filled': True}}
    nx.set_node_attributes(graph, node_res_map)

    return graph


def fill_graph_with_leaves(graph_with_leaves):
    next_nodes = nodes_to_evaluate_next(graph_with_leaves)
    if not next_nodes:
        return graph_with_leaves

    for node in next_nodes:
        graph_with_leaves = evaluate_node(graph_with_leaves, node)

    return fill_graph_with_leaves(graph_with_leaves)


def fill_graph(graph, rootns):
    graph_with_leaves = fill_leaves(graph, rootns)
    full_graph = fill_graph_with_leaves(graph_with_leaves)
    return full_graph


def solution(filled_graph, base_nodes, parallel=False):
    node_data = nx.get_node_attributes(filled_graph, 'value')

    name_solution_map = {}
    for base_node in base_nodes:
        if parallel:
            # XXX: this possibly computes from scratch each node we request...
            name_solution_map[base_node.name] = node_data[base_node].compute()
        else:
            name_solution_map[base_node.name] = node_data[base_node]

    return name_solution_map
