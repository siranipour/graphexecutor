from graphbuilder import *
from graphexecutor import *

if __name__ == '__main__':
    # base_nodes = [FunctionNode(actions.some_other_action),]
    # interesting disjoint graph example:
    base_nodes = [FunctionNode(actions.some_other_action), FunctionNode(actions.bar)]
    # base_nodes = [FunctionNode(actions.cycle)]
    # look into nx.strongly_connected_components
    graph = actions_to_graph(base_nodes)

    rootns = {'num': 5, 'foo': 2, 'baz': 5, 'y': 10} # Would read this from the runcard
    final_graph = add_solution_node(graph, base_nodes)
    delayed_graph = to_delayed_graph(final_graph)
    filled_graph = fill_graph(delayed_graph, rootns)

    sol = solution(filled_graph, True)
