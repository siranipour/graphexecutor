import logging
import networkx as nx


from graphexecutor import graphbuilder as gb
from graphexecutor import graphrunner as gr

class CycleError(Exception): pass


class MissingParameterError(Exception): pass


def format_node_path(node_path_map):
    msg = "The following keys are missing:\n"
    for node, path in node_path_map.items():
        msg += f'- {node} through: '
        msg += ' -> '.join(path)
        msg += '\n\n'
    msg = msg[:-1]
    return msg

def check_bare_graph_against_runcard(graph, rootns):
    needed_nodes = gb.graph_leaves(graph)
    needed_keys = set([node.name for node in needed_nodes])

    missing_keys = needed_keys.difference(rootns.keys())
    missing_nodes = [node for node in needed_nodes if node.name in missing_keys]

    solution_node = gb.find_solution_node(graph)

    node_path_map = {}
    for node in missing_nodes:
        # Don't expose solution node to user
        path = nx.shortest_path(graph, solution_node, node)[1:]
        path = [node.name for node in path]
        node_path_map[node.name] = path

    extra_keys = gr.unused_keys(graph, rootns)

    if missing_keys:
        msg = format_node_path(node_path_map)
        raise MissingParameterError(msg)

    if extra_keys:
        logging.warning(f"The following are unused keys: {extra_keys}")


def check_for_cycles(graph):
    cycles = list(nx.simple_cycles(graph))
    for idx, cycle in enumerate(cycles):
        cycles[idx] = [node.name for node in cycle]
    if cycles:
        raise CycleError(
            "The following cyclic dependencies exist "
            f"in the dependency graph {cycles}"
            )
    return graph