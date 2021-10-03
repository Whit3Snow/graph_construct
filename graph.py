class Node():
    def __init__(self, name):
        self.name = name
        self.lower_nodes = None
        self.higher_nodes = None

        self.edges = []
        self.parent_edges = []

        self.optional = False
    
    def add_lower(self, obj):
        self.lower_nodes.append(obj)

    def add_higher(self, obj):
        self.higher_nodes.append(obj)

    def add_edge(self, obj, edge_type):
        self.edges.append((self, obj, edge_type))
        obj.parent_edges.append((obj, self, edge_type))
    
    def remove_lower(self, obj):
        self.lower_nodes.remove(obj)
    
    def remove_higher(self, obj):
        self.higher_nodes.remove(obj)

    def empty_lowers(self):
        self.lower_nodes = []

    def update_lower_nodes(self, new_nodes):
        self.lower_nodes = new_nodes

    def empty_highers(self):
        self.higher_nodes = []
    
    def get_lowers(self):
        return self.lower_nodes
    
    def get_highers(self):
        return self.higher_nodes

    def get_edges(self):
        return self.edges

    def get_edge_c_nodes(self):
        return [edge for (_, edge, _) in self.edges]

    def get_parent_edges(self):
        return self.parent_edges

    def num_lowers(self):
        return len(self.lower_nodes)

    def num_highers(self):
        return len(self.higher_nodes)

    def has_edge(self, t_node, target_edge_type):
        for p_node, c_node, edge_type in self.edges:
            if c_node == t_node and edge_type in target_edge_type:
                return True
        return False

    def remove_edge(self, t_node, target_edge_type):
        for cur_edge in self.edges:
            p_node, c_node, edge_type = cur_edge
            if c_node == t_node and edge_type == target_edge_type:
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

    def set_optional(self):
        self.optional = True

    def is_optional(self):
        return self.optional

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