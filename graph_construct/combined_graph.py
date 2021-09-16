import networkx as nx
import matplotlib.pyplot as plt
import math
from graph import *
import random
import individual_graph

high_level_nodes = ["cut_and_mix_ingredients", "prepare_dressing", "serve_salad"]

def get_action_list(annotation_file):
    f = open(annotation_file, 'r')
    lines = f.readlines()
    f.close()

    all_actions = []
    for line in lines:
        tokens = line.split(' ')
        start_time = tokens[0]
        action_name = tokens[2][:-1]
        if action_name not in high_level_nodes:
            all_actions.append([start_time, action_name])
    all_actions = sorted(all_actions, key=lambda x : int(x[0]))

    refined_actions = []
    for _, action_name in all_actions:
        action_split = action_name.split('_')
        if action_split[-1] in ['core', 'prep', 'post']:
            action_name = "_".join(action_split[:-1])
        if len(refined_actions) == 0 or refined_actions[-1] != action_name:
            refined_actions.append(action_name) 
    refined_actions.append("done")

    return refined_actions

def hierarchy_pos_1(G, root=None, width=2., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    # From https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3/29597209#29597209
    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, done=[]):
        if pos is None:
            pos = {root:(xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        rem_children = _remaining_children(children, done)
        if len(rem_children) != 0:
            dx = width/len(rem_children) 
            nextx = xcenter - width/2 - dx/2
            for child in rem_children:
                nextx += dx
                done.append(child)
                pos = _hierarchy_pos(G, child, width=width, vert_gap=vert_gap, 
                                    vert_loc=vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent=root, done=done)
        return pos

    def _remaining_children(children, done):
        return [c for c in children if c not in done]

    # levels = _make_levels({}, root)
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def hierarchy_pos_2(G, root=None, levels=None, width=1., height=1.):
    # from https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3/29597209#29597209

    def make_levels(levels, node, currentLevel=0, parent=None, done=[]):
        if not currentLevel in levels:
            levels[currentLevel] = {"total" : 0, "current" : 0}
        levels[currentLevel]["total"] += 1
        neighbors = list(G.neighbors(node))
        rem_neighbors = remaining_neighbors(neighbors, done)
        for neighbor in rem_neighbors:
            if not neighbor == parent:
                done.append(neighbor)
                levels =  make_levels(levels, neighbor, currentLevel + 1, node, done)
        return levels

    def make_pos(pos, node, currentLevel=0, parent=None, vert_loc=0, done=[]):
        dx = 1/levels[currentLevel]["total"]
        left = dx/2
        pos[node] = ((left + dx*levels[currentLevel]["current"])*width, vert_loc)
        levels[currentLevel]["current"] += 1
        neighbors = list(G.neighbors(node))
        rem_neighbors = remaining_neighbors(neighbors, done)
        for neighbor in rem_neighbors:
            if not neighbor == parent:
                done.append(neighbor)
                pos = make_pos(pos, neighbor, currentLevel + 1, node, vert_loc-vert_gap)
        return pos

    def remaining_neighbors(neighbors, done):
        return [n for n in neighbors if n not in done]

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    if levels is None:
        levels = make_levels({}, root)
    else:
        levels = {l:{"total": levels[l], "current":0} for l in levels}

    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({}, root)

def construct_graph(all_action_list):
    graph = Graph()
    for action_list in all_action_list:
        for idx, name in enumerate(action_list):
            cur_node = graph.get_node(name)
            if cur_node == False:
                cur_node = Node(name)
                if idx > 0:
                    child_name = action_list[idx-1]
                    child_node = graph.get_node(child_name)
                    cur_node.add_child(child_node)
                    child_node.add_parent(cur_node)
                graph.add_node(cur_node)
            else:
                if cur_node.is_leaf():
                    continue
                elif idx == 0:
                    for child_node in cur_node.get_childs():
                        child_node.remove_parent(cur_node)
                        # cur_node.add_mutex(child_node)
                        # child_node.add_mutex(cur_node)
                    cur_node.empty_childs()
                elif idx > 0:
                    child_name = action_list[idx-1]
                    child_node = graph.get_node(child_name)
                    if child_node in cur_node.get_parents() + cur_node.get_childs():
                        continue
                        # cur_node.remove_parent(child_node)
                        # child_node.remove_child(cur_node)
                        # cur_node.add_mutex(child_node)
                        # child_node.add_mutex(cur_node)
                    if child_node not in cur_node.get_mutex() and cur_node not in child_node.get_mutex():
                        cur_node.add_child(child_node)
                        child_node.add_parent(cur_node)
    return graph

def draw_graph(graph):
    f = plt.figure(figsize=(GRAPH_WIDTH, GRAPH_WIDTH))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.DiGraph()

    for i, node in enumerate(graph.get_node_list()):
        DG.add_node(node.name, name=node.name)

    for i, node in enumerate(graph.get_node_list()):
        for child in node.get_childs():
            style = 'dashed' if node.num_childs() > 1 else 'solid'
            DG.add_edge(node.name, child.name, style=style)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)
    pos = hierarchy_pos_1(DG)
    # pos = nx.kamada_kawai_layout(DG)

    nx.draw_networkx_nodes(DG, pos=pos)

    edge_dashed = [(u, v) for (u, v, d) in edgelist if d["style"] == 'dashed']
    edge_solid = [(u, v) for (u, v, d) in edgelist if d["style"] != 'dashed']
    nx.draw_networkx_edges(DG, pos=pos, edgelist=edge_dashed, style='dashed', edge_color="green")
    nx.draw_networkx_edges(DG, pos=pos, edgelist=edge_solid, edge_color="red")
    
    labels = nx.get_node_attributes(DG, 'name')
    description = nx.draw_networkx_labels(DG, pos=pos, labels=labels, font_size=FONT_SIZE)
    for node, t in description.items():
        t.set_rotation(LABEL_ROTATION)
    plt.box(False)

    plt.savefig("graphs.png")

'''
Hyper-parameters
'''
LABEL_ROTATION = 10
GRAPH_WIDTH = 10
FONT_SIZE = 8
EDGE_COLOR = "green"
plot_list = ["01-1", "01-2", "03-1"]
# plot_list = ["01-1", "03-1"]
# plot_list = ["02-1"]
# plot_list = ["{:02}-{}".format(i, j) for i in range(1,28) for j in [1, 2]][:3]

individual_graph.main(plot_list)

all_action_list = []
for idx, plot_file in enumerate(plot_list):
    all_action_list.append(get_action_list("../activityAnnotations/{}-activityAnnotation.txt".format(plot_file)))

graph_object = construct_graph(all_action_list)
draw_graph(graph_object)
