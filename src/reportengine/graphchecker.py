import functools

import networkx as nx

import graphbuilder as gb
import graphexecutor as ge


class CycleError(Exception): pass


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

    extra_keys = ge.unused_keys(graph, rootns)

    if missing_keys:
        raise KeyError(
                f"The following keys are missing: {list(node_path_map.keys())} "
                f"through {list(node_path_map.values())}"
            )

    if extra_keys:
        print(f"WARNING: The following are unused keys: {extra_keys}")


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

