import random 

class Node():
    def __init__(self, name):
        self.name = name
        self.lower_nodes = []

        self.edges = []
        self.rep = False

        #For probability
        self.lower_nums = {'add_dressing':0, 'serve_salad_onto_plate':0, 'mix_dressing' : 0, 'mix_ingredients': 0,
            'add_salt':0, 'add_pepper': 0, 'place_lettuce_into_bowl':0, 'place_cheese_into_bowl':0, 'place_tomato_into_bowl': 0, 'place_cucumber_into_bowl' : 0,
            'add_vinegar':0, 'add_oil':0, 'cut_lettuce':0, 'cut_cheese':0, 'cut_tomato': 0, 'cut_cucumber': 0,
            'peel_cucumber':0 }
        
    def get_lower_nums(self):
        return self.lower_nums

    def add_lower(self, obj):
        self.lower_nums[obj] += 1

    def empty_lower_nums(self):
        
        self.lower_nums = {'add_dressing':0, 'serve_salad_onto_plate':0, 'mix_dressing' : 0, 'mix_ingredients': 0,
            'add_salt':0, 'add_pepper': 0, 'place_lettuce_into_bowl':0, 'place_cheese_into_bowl':0, 'place_tomato_into_bowl': 0, 'place_cucumber_into_bowl' : 0,
            'add_vinegar':0, 'add_oil':0, 'cut_lettuce':0, 'cut_cheese':0, 'cut_tomato': 0, 'cut_cucumber': 0,
            'peel_cucumber':0 }
        

    def add_lower_list(self, obj):
        self.lower_nodes.append(obj)


    def add_edge(self, obj, edge_type):
        self.edges.append((self, obj, edge_type))

    def empty_lowers(self):
        self.lower_nodes = []

    def update_lower_nodes(self, new_nodes):
        self.lower_nodes = new_nodes

    
    def get_lowers(self):
        if self.lower_nodes:
            random.shuffle(self.lower_nodes)
        return self.lower_nodes

    def get_edges(self):
        random.shuffle(self.edges)
        return self.edges

    def remove_edge(self, t_node, t_edge_type):
        for cur_edge in self.edges:
            p_node, c_node, edge_type = cur_edge
            if c_node == t_node and edge_type == t_edge_type:
                self.edges.remove(cur_edge)
                break
    
    def is_connected(self, t_node, visited_nodes=[], ignored_edges=[], target_edge_types=[]):
        if self == t_node:
            return True
        for edge in self.edges:
            p_node, c_node, edge_type = edge
            if edge in ignored_edges:
                continue
            if len(target_edge_types) > 0 and edge_type not in target_edge_types:
                continue
            if c_node in visited_nodes:
                continue
            visited_nodes.append(c_node)
            if c_node.is_connected(t_node, visited_nodes, ignored_edges, target_edge_types):
                return True
        return False

    def get_lower_nodes(self):
        return [node for _, node, edge_type in self.get_edges() if edge_type=='lower']

    def __str__(self):
        return self.name

class Graph():
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)
    
    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return False

    def is_empty(self):
        return len(self.nodes) == 0

    def get_node_list(self):
        return self.nodes