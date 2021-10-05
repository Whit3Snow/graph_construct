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

class GraphRunner():
    def __init__(self, graph, action_list=None):
        self.orig_graph = graph
        self.graph = copy.deepcopy(graph)
        self.action_list = action_list
        self.action_idx = 0
        self.action_log = []
        self.test_video = action_list != None

    def draw_graph(self):
        if self.test_video:
            return
        from combined_graph import draw_graph
        draw_graph(self.graph)

    def run(self):
        self.update_node_states()
        done_node = self.graph.get_node('done')
        while not self.is_complete(done_node):
            self.draw_graph()
            self.show_executable_nodes()
            next_action = self.get_next_action()
            while not next_action:
                next_action = self.get_next_action()
            self.execute_node(next_action)
            
        self.draw_graph()
        print('\nDone! Executed actions:')
        for action in self.action_log:
            print(action, end=', ')

    def print_nodes(self, nodes):
        print("Executable nodes: ", end='')
        for node in nodes:
            print(node, end=', ')
        print()

    def get_next_action(self):
        if self.test_video:
            action = self.action_list[self.action_idx]
            self.action_idx += 1
            print("Node to execute: " + action)
        else:
            action = input("Node to execute: ")
        action_node = self.graph.get_node(action)

        if not action_node:
            return False
        
        if not self.is_executable(action_node):
            print("Node {} is not executable!".format(action_node.name))
            return False

        self.action_log.append(action_node)
        return action_node

    def execute_node(self, node):
        node.executed = True
        self.update_node_states()

    def show_executable_nodes(self):
        executable_nodes = [node for node in self.graph.get_node_list() if self.is_executable(node)]
        self.print_nodes(executable_nodes)

    def update_node_states(self):
        changed = True
        while changed:
            changed = False
            for i, node in enumerate(self.graph.get_node_list()):
                new_state = 0
                if self.is_finished(node):
                    new_state = 3
                elif self.is_complete(node):
                    new_state = 2
                elif self.is_executable(node):
                    new_state = 1
                if node.state != new_state:
                    changed = True
                    node.state = new_state

    def is_executable(self, node):
        if node.state > 2:
            return False
        for a_node in node.get_after_nodes():
            if a_node.executed:
                return False
        for c_node in node.get_lower_nodes():
            if c_node.state < 2:
                return False
        return True

    def is_complete(self, node):
        if not node.is_optional() and not node.executed:
            return False
        for c_node in node.get_mandatory_nodes(): # CHECK
            if c_node.state < 2:
                return False
        return True

    def is_finished(self, node):
        for c_node in node.get_mandatory_nodes():
            if c_node.state < 2:
                return False
        for a_node in node.get_after_nodes():
            if a_node.executed or a_node.state > 2:
                return True
        return False