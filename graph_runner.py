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
    def __init__(self, graph, all_action_list):
        self.orig_graph = graph
        self.graph = copy.deepcopy(graph)
        self.all_action_list = all_action_list
        self.cur_action_list_idx = 0
        self.cur_action_list = all_action_list[self.cur_action_list_idx]
        self.cur_action_idx = 0

    def reset(self):
        self.graph = copy.deepcopy(self.orig_graph)
        self.cur_action_list_idx += 1
        self.cur_action_idx = 0

    def run(self):
        from combined_graph import draw_graph
        for action_list in self.all_action_list:
            self.update_node_states()
            runnable_nodes = self.get_runnable_nodes()
            done_node = self.graph.get_node('done')
            while not self.is_complete(done_node):
                draw_graph(self.graph)
                self.print_nodes(runnable_nodes)
                choice = self.get_next_action()
                choice_node = self.graph.get_node(choice)
                self.execute_node(choice_node)
                self.update_node_states()
                runnable_nodes = self.get_runnable_nodes()
            draw_graph(self.graph)
            input('Next?')
            self.reset()

    def print_nodes(self, nodes):
        for node in nodes:
            print(node, end=', ')
        print()

    def get_next_action(self):
        action = input()
        # action = self.cur_action_list[self.cur_action_idx]
        # self.cur_action_idx += 1
        # print(action)

        return action

    def execute_node(self, node):
        if not self.is_executable(node):
            print("Not executable! Current state of node {} is {}!".format(node.name, node.state))
            return
                
        node.executed = True

    def get_runnable_nodes(self):
        return [node for node in self.graph.get_node_list() if self.is_executable(node)]

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