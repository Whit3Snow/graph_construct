from graph import *
import copy

"""
Node explanation:
A node can be EXECUTED if:
    1. no green-parent nodes are EXECUTED
    2. all red-child nodes are COMPLETE
    
A blue node is COMPLETE if:
    1. the node is EXECUTED
    2. all red-child nodes are COMPLETE
    3. all black-child nodes are COMPLETE

A grey node is COMPLETE if:
    1. all red-child nodes are COMPLETE
    2. all black-child nodes are COMPLETE
    
# A blue node is FINISHED if:
#     1. any green-parent nodes are EXECUTED
#     2. all red-child nodes are COMPLETE
#     3. all black-child nodes are COMPLETE

"""
def run_graph(graph):
    from combined_graph import draw_graph
    graph = copy.deepcopy(graph)
    update_node_states(graph)
    runnable_nodes = get_runnable_nodes(graph)
    done_node = graph.get_node('done')
    while not is_complete(done_node):
        draw_graph(graph)
        print_nodes(runnable_nodes)
        choice = input()
        choice_node = graph.get_node(choice)
        execute_node(choice_node)
        update_node_states(graph)
        runnable_nodes = get_runnable_nodes(graph)

def print_nodes(nodes):
    for node in nodes:
        print(node, end=', ')
    print()

def execute_node(node):
    if not is_executable(node):
        print("Not executable! Current state of node {} is {}!".format(node.name, node.state))
        return
    node.executed = True

def get_runnable_nodes(graph):
    return [node for node in graph.get_node_list() if is_executable(node)]

def update_node_states(graph):
    for i, node in enumerate(graph.get_node_list()):
        if is_finished(node):
            node.state = 3
        elif is_complete(node):
            node.state = 2
        elif is_executable(node):
            node.state = 1

def is_executable(node):
    for a_node in node.get_after_nodes():
        if a_node.executed:
            return False
    for c_node in node.get_required_nodes():
        if c_node.state < 2:
            return False
    return True

def is_complete(node):
    if not node.is_optional() and not node.executed:
        return False
    for c_node in node.get_required_nodes():
        if c_node.state < 2:
            return False
    return True

def is_finished(node):
    for c_node in node.get_required_nodes():
        if c_node.state < 2:
            return False
    for a_node in node.get_after_nodes():
        if a_node.executed:
            return True
    return False