import yaml

from graphbuilder import actions_to_graph, FUNCTION_MAPPING, FunctionNode
from graphexecutor import (
    fill_graph,
    to_delayed_graph,
    graph_solution,
    required_keys,
    unused_keys,
)


def read_input(path):
    with open(path, 'r') as stream:
        runcard = yaml.safe_load(stream)
    return runcard


def action_to_function(action: str):
    try:
        return FUNCTION_MAPPING[action]
    except KeyError:
        raise KeyError(f"The action {action} could not be found")


def runcard_rootns(runcard):
    actionless_dict = {}
    for k, v in runcard.items():
        if k == 'actions':
            continue
        actionless_dict[k] = v
    return actionless_dict


def check_bare_graph_against_runcard(graph, rootns):
    needed_keys = required_keys(graph)
    extra_keys = unused_keys(graph, rootns)

    missing_keys = needed_keys.difference(rootns.keys())

    if missing_keys:
        raise KeyError(f"The following keys are missing: {missing_keys}")

    if extra_keys:
        print(f"WARNING: The following are unused keys: {extra_keys}")


def bare_graph_from_runcard(runcard):
    try:
        actions = runcard['actions']
    except KeyError:
        raise KeyError("Runcard needs to define actions namespace")

    if not isinstance(actions, list):
        raise TypeError(f"The actions namespace must be a list not {type(actions)}")

    actions = list(map(lambda x: FunctionNode(action_to_function(x)), actions))

    graph = actions_to_graph(actions)


    return graph


def filled_graph_from_runcard(runcard, parallel):
    rootns = runcard_rootns(runcard)

    bare_graph = bare_graph_from_runcard(runcard)
    check_bare_graph_against_runcard(bare_graph, rootns)

    if parallel:
        bare_graph = to_delayed_graph(bare_graph)

    graph_with_values = fill_graph(bare_graph, rootns)

    return graph_with_values


def execute_runcard(path, parallel=False):
    runcard = read_input(path)
    graph = filled_graph_from_runcard(runcard, parallel)

    sol = graph_solution(graph, parallel)

    return sol
