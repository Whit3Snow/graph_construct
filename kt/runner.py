from graph import *
import copy
import json

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
        self.action_log_human = []
        self.action_log_robot = []
        self.METADATA = json.load(open('metadata.json'))
        self.set_node_objects()
    
    def set_node_objects(self):
        for action in self.METADATA["ACTIONS"]:
            node = self.graph.get_node(action)
            node.objects = self.METADATA["OBJECTS"][action]

    def draw_graph(self):
        from main import draw_graph
        draw_graph(self.graph, self.METADATA["POS"])

    def run(self):
        self.update_node_states()
        end_node = self.graph.get_node('end')
        
        while not self.is_complete(end_node):
            self.draw_graph()
            self.show_executable_nodes()
            human_action = self.get_next_action()
            while not human_action:
                human_action = self.get_next_action()
            time_left = human_action.time
            while time_left >= 0:
                robot_action = self.get_next_action_robot(time_left)
                if robot_action != False:
                    time_left -= robot_action.time
                    self.execute_node(robot_action)
                    self.draw_graph()
                else:
                    break
            self.execute_node(human_action)
                
        self.draw_graph()
        print('\nDone! Executed actions:')
        for action in self.action_log_robot:
            print(action, end=', ')

    def print_nodes(self, nodes):
        print("Executable nodes: ", end='')
        for node in nodes:
            print(node, end=', ')
        print()

    def get_next_action(self):
        action = input("Node to execute by human: ")
        if action == "q":
            exit()
        action_node = self.graph.get_node(action)

        if not action_node:
            return False
        
        if not self.is_executable(action_node):
            print("Node {} is not executable!".format(action_node.name))
            return False

        self.action_log_human.append(action_node)
        return action_node

    def get_next_action_robot(self, time):
        executable_nodes = [node for node in self.graph.get_node_list() if self.is_executable(node)]
        executable_nodes.sort(key=lambda x : x.time, reverse=True)
        human_action = self.action_log_human[-1]
        
        time_suggestion = list()
        for e_node in executable_nodes:
            if (e_node.time <= time and not e_node.executed):
                time_suggestion.append(e_node)
        t_s_suggestion = list()
        for node in time_suggestion:
            fail = False
            for item in human_action.objects:
                if item in node.objects:
                    fail = True
                    break
            if not fail:
                t_s_suggestion.append(node)
        t_s_d_suggestion = list()
        all_parents = self.get_all_parents(human_action)
        for node in t_s_suggestion:
            distance = self.check_distance(all_parents, node)
            t_s_d_suggestion.append((node, distance))
        t_s_d_suggestion.sort(key=lambda x : x[1], reverse=True)
        final_suggestion = list()
        if (len(t_s_d_suggestion) != 0):
            max_distance = t_s_d_suggestion[0][1]
            for node, d in t_s_d_suggestion:
                if (d < max_distance):
                    break
                final_suggestion.append(node)

        if (len(final_suggestion) != 0):
            final_suggestion.sort(key=lambda x : x.time)
            action_node = final_suggestion[0]
            print("robot executes " + action_node.name)
            self.action_log_robot.append(action_node)
            return action_node
        else:
            return False
    
    
    def get_all_parents(self, node):
        if node.name == "end":
            return list()
        all_parents = list()
        node_info = node.get_parent_edges()
        distance = 1
        while (not len(node_info) == 0):
            next_level = list()
            for _, node, t in node_info:
                if t == "lower":
                    all_parents.append((node, distance))
                    if node.name != "end":
                        next_level.append(node.get_parent_edges())
            distance += 1
            empty_list = list()
            for node_set in next_level:
                for node in node_set:
                    empty_list.append(node)
            node_info = empty_list
        return all_parents
            
    def check_distance(self, all_parents, tbd_node):
        target_parents = self.get_all_parents(tbd_node)
        min_distance = 10**3
        same_name = ""
        for node0, dis0 in all_parents:
            for node1, dis1 in target_parents:
                distance = dis0 + dis1
                if (node1.name == node0.name) and (distance < min_distance):
                    same_name = node0.name
                    distance = dis0 + dis1
                    min_distance = distance
        return min_distance

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