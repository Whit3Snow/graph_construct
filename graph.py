import random 

class Node():
    def __init__(self, name):
        self.name = name
        self.lower_nodes = None
        self.higher_nodes = None
        self.after_nodes = []

        self.edges = []
        self.parent_edges = []

        self.optional = False

        # For running
        self.state = 0
        self.executed = False
    
    def add_lower(self, obj):
        self.lower_nodes.append(obj)

    def add_higher(self, obj):
        self.higher_nodes.append(obj)

    def add_after(self, obj):
        self.after_nodes.append(obj)

    def add_edge(self, obj, edge_type):
        self.edges.append((self, obj, edge_type))
        obj.parent_edges.append((obj, self, edge_type))

    def empty_lowers(self):
        self.lower_nodes = []

    def update_lower_nodes(self, new_nodes):
        self.lower_nodes = new_nodes

    def empty_highers(self):
        self.higher_nodes = []

    def update_higher_nodes(self, new_nodes):
        self.higher_nodes = new_nodes
    
    def get_lowers(self):
        if self.lower_nodes:
            random.shuffle(self.lower_nodes)
        return self.lower_nodes
    
    def get_highers(self):
        if self.higher_nodes:
            random.shuffle(self.higher_nodes)
        return self.higher_nodes
    
    def get_afters(self):
        if self.after_nodes:
            random.shuffle(self.after_nodes)
        return self.after_nodes

    def finalize_afters(self, all_nodes):
        self.after_nodes = list(set(all_nodes)-set(self.get_afters())-set([self]))
        return self.after_nodes

    def get_edges(self):
        random.shuffle(self.edges)
        return self.edges

    def get_edge_c_nodes(self):
        return [edge for (_, edge, _) in self.edges]

    def get_parent_edges(self):
        random.shuffle(self.parent_edges)
        return self.parent_edges

    def remove_edge(self, t_node, t_edge_type):
        for cur_edge in self.edges:
            p_node, c_node, edge_type = cur_edge
            if c_node == t_node and edge_type == t_edge_type:
                self.edges.remove(cur_edge)
                c_node.remove_parent_edge(self, t_edge_type)
                break
                
    def remove_parent_edge(self, t_node, t_edge_type):
        for cur_edge in self.parent_edges:
            c_node, p_node, edge_type = cur_edge
            if p_node == t_node and edge_type == t_edge_type:
                self.parent_edges.remove(cur_edge)
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

    def set_optional(self):
        self.optional = True

    def is_optional(self):
        return self.optional

    def get_required_nodes(self):
        return [node for node in self.get_edge_c_nodes() if self.requires(node)]

    def get_lower_nodes(self):
        return [node for _, node, edge_type in self.get_edges() if edge_type=='lower']

    def get_higher_parent_nodes(self):
        return [node for node, _, edge_type in self.get_parent_edges() if edge_type=='higher' or edge_type=='new']

    def get_mandatory_nodes(self):
        return [node for _, node, edge_type in self.get_edges() if edge_type=='lower' or edge_type=='new']

    def get_after_nodes(self):
        return [node for _, node, edge_type in self.get_edges() if edge_type=='after']

    def requires(self, t_node):
        connected = self.is_connected(t_node, visited_nodes=[], target_edge_types=['lower', 'new'])
        optional = t_node.is_optional()
        return connected and not optional

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