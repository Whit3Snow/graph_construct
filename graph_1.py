class Node():
    def __init__(self, name):
        self.name = name
        self.child_nodes = []
        self.lower_nodes = []
        self.higher_nodes = None

        self.edges = []
        self.parent_edges = []

    def add_child(self, obj):
        self.child_nodes.append(obj)
    
    def add_lower(self, obj):
        self.lower_nodes.append(obj)

    def add_higher(self, obj):
        self.higher_nodes.append(obj)

    def add_edge(self, obj, edge_type):
        self.edges.append((self, obj, edge_type))
        obj.parent_edges.append((obj, self, edge_type))

    def remove_child(self, obj):
        self.child_nodes.remove(obj)
    
    def remove_lower(self, obj):
        self.lower_nodes.remove(obj)
    
    def remove_higher(self, obj):
        self.higher_nodes.remove(obj)

    def empty_childs(self):
        self.child_nodes = []

    def empty_lowers(self):
        self.lower_nodes = []

    def update_child_nodes(self, new_nodes):
        self.child_nodes = new_nodes

    def update_lower_nodes(self, new_nodes):
        self.lower_nodes = new_nodes

    def empty_highers(self):
        self.higher_nodes = []

    def get_childs(self):
        return self.child_nodes
    
    def get_lowers(self):
        return self.lower_nodes
    
    def get_highers(self):
        return self.higher_nodes

    def get_edges(self):
        return self.edges

    def get_edge_cnodes(self):
        return [edge for (_, edge, _) in self.edges]

    def get_parent_edges(self):
        return self.parent_edges

    def num_childs(self):
        return len(self.child_nodes)

    def num_lowers(self):
        return len(self.lower_nodes)

    def num_highers(self):
        return len(self.higher_nodes)

    def is_leaf(self):
        return len(self.child_nodes) == 0

    def has_edge(self, tnode, target_edge_type):
        for pnode, cnode, edge_type in self.edges:
            if cnode == tnode and edge_type in target_edge_type:
                return True
        return False

    def remove_edge(self, tnode, target_edge_type):
        for cur_edge in self.edges:
            pnode, cnode, edge_type = cur_edge
            if cnode == tnode and edge_type == target_edge_type:
                self.edges.remove(cur_edge)
                break

    def is_connected(self, tnode, visited_nodes=[], ignored_edges=[], target_edge_types=[]):
        if self == tnode:
            return True
        for edge in self.edges:
            pnode, cnode, edge_type = edge
            if edge in ignored_edges:
                continue
            if len(target_edge_types) > 0 and edge_type not in target_edge_types:
                continue
            if cnode in visited_nodes:
                continue
            visited_nodes.append(cnode)
            if cnode.is_connected(tnode, visited_nodes, ignored_edges, target_edge_types):
                return True
        return False

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

    def get_node_list(self, func=lambda x : x.num_lowers()):
        # self.nodes = sorted(self.nodes, key=func)
        return self.nodes