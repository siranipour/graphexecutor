import yaml

from graphexecutor.graphbuilder import actions_to_graph, FunctionNode
from graphexecutor.graphchecker import check_bare_graph_against_runcard
from graphexecutor.graphrunner import (
    fill_graph,
    to_delayed_graph,
    graph_solution,
)


def read_input(path):
    with open(path, 'r') as stream:
        runcard = yaml.safe_load(stream)
    return runcard


def action_to_function(action: str, spec_func_map):
    try:
        return spec_func_map[action]
    except KeyError:
        raise KeyError(f"The action {action} could not be found")


def runcard_rootns(runcard):
    actionless_dict = {}
    for k, v in runcard.items():
        if k == 'actions':
            continue
        actionless_dict[k] = v
    return actionless_dict


def bare_graph_from_runcard(runcard, spec_func_map):
    try:
        actions = runcard['actions']
    except KeyError:
        raise KeyError("Runcard needs to define actions namespace")

    if not isinstance(actions, list):
        raise TypeError(f"The actions namespace must be a list not {type(actions)}")

    actions = list(map(lambda x: FunctionNode(action_to_function(x, spec_func_map)), actions))

    graph = actions_to_graph(actions, spec_func_map)


    return graph


def filled_graph_from_runcard(runcard, spec_func_map, parallel):
    rootns = runcard_rootns(runcard)

    bare_graph = bare_graph_from_runcard(runcard, spec_func_map)
    check_bare_graph_against_runcard(bare_graph, rootns)

    if parallel:
        bare_graph = to_delayed_graph(bare_graph)

    graph_with_values = fill_graph(bare_graph, rootns)

    return graph_with_values


def graph_from_path(path, parallel):
    runcard = read_input(path)
    return filled_graph_from_runcard(runcard, parallel)


def execute_runcard(path, spec_func_map, parallel):
    runcard = read_input(path)
    graph = filled_graph_from_runcard(runcard, spec_func_map, parallel)

    sol = graph_solution(graph, parallel)

    return sol
