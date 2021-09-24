import networkx as nx
import matplotlib.pyplot as plt
import math
import numpy as np
from graph_1 import *
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

def hierarchy_pos_1(G, root=None, width=5., vert_gap=2., vert_loc=0, xcenter=5):
    # From https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3/29597209#29597209
    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter, pos=None, parent=None, done=[]):
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
                pos = _hierarchy_pos(G, child, width=width, vert_gap=1, 
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
        levels = {l:{"total": levels[l], "current": 0} for l in levels}

    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({}, root)


def hierarchy_pos_3(G, root):

    def remaining_neighbors(neighbors):
        return [n for n in neighbors if n not in list(done.keys())]
    
    node_list = [root]
    done = {}
    done[root] = 0
    level = {}
    level[0] = [1, 0]

    for node in node_list:
        cur_level = done[node]
        child_nodes = list(G.neighbors(node))
        child_nodes = sorted(child_nodes, key=lambda x : -len(list(G.neighbors(x))))
        cur_child_cnt = -1
        cur_child_level = cur_level
        for child in remaining_neighbors(child_nodes):
            child_cnt = len(list(G.neighbors(child)))
            if cur_child_cnt < 0 or cur_child_cnt != child_cnt:
                cur_child_cnt = child_cnt
                cur_child_level += 1
                if cur_child_level not in level:
                    level[cur_child_level] = [0, 0]
            done[child] = cur_child_level
            level[cur_child_level][0] += 1
            node_list.append(child)
    
    print(done)
    print(level)

    max_level_cnt = max(list(level.values()))[0]
    pos = {}
    for node in done:
        y = done[node]
        level_cnt, idx = level[y]
        if level_cnt == 1:
            x = 0
        else:
            step = max_level_cnt/(level_cnt-1)
            start = -max_level_cnt/2
            end = max_level_cnt/2+1
            float_range_array = list(np.arange(start, end, step))
            x = float_range_array[idx]
        level[y][1] += 1
        pos[node] = (x, -y)
    return pos


def construct_graph(all_action_list):
    graph = Graph()
    for action_list in all_action_list:
        for idx, name in enumerate(action_list):
            cur_node = graph.get_node(name)
            if cur_node == False:
                cur_node = Node(name)
                if idx > 0:
                    for lower_name in action_list[:idx]:
                        lower_node = graph.get_node(lower_name)
                        if lower_node not in cur_node.get_lowers():
                            cur_node.add_lower(lower_node)
                    if CHILD:
                        child_node = graph.get_node(action_list[idx-1])
                        cur_node.add_child(child_node)
                graph.add_node(cur_node)
            else:
                if idx == 0:
                    cur_node.empty_childs()
                    cur_node.empty_lowers()
                elif idx > 0:
                    updated_lowers = [lower_node for lower_node in cur_node.get_lowers() if lower_node.name in action_list[:idx]]
                    cur_node.update_lower_nodes(updated_lowers)
                    if CHILD:
                        updated_childs = [child_node for child_node in cur_node.get_childs() if child_node in cur_node.get_lowers()]
                        cur_node.update_child_nodes(updated_childs)
                        
                        child_name = action_list[idx-1]
                        child_node = graph.get_node(child_name)
                        if (child_node not in cur_node.get_childs()) and (child_node in cur_node.get_lowers()):
                            cur_node.add_child(child_node)

        for idx, name in enumerate(action_list):
            cur_node = graph.get_node(name)
            if cur_node.get_highers() == None:
                cur_node.empty_highers()
                for higher_name in action_list[idx+1:]:
                    higher_node = graph.get_node(higher_name)
                    if higher_node not in cur_node.get_highers():
                        cur_node.add_higher(higher_node)
            else:
                updated_highers = [higher_node for higher_node in cur_node.get_highers() if higher_node.name in action_list[idx+1:]]
                cur_node.higher_nodes = updated_highers

    return graph

def reconstruct_graph(graph):
    for i, node in enumerate(graph.get_node_list()):
        for child in node.get_childs():
            node.add_edge(child, 'child')
        
    for i, node in enumerate(graph.get_node_list()):
        for lower in node.get_lowers():
            if lower not in node.get_edge_nodes() and not node.can_reach(lower, []):
                node.add_edge(lower, 'lower')

    for i, node in enumerate(graph.get_node_list(lambda x : x.num_highers())):
        for higher in node.get_highers():
            if node not in higher.get_edge_nodes() and not higher.can_reach(node, []):
                higher.add_edge(node, 'higher')
                reconstruct_list = []
                for parent, edge_type in node.get_edge_parents():
                    if parent.has_edge(node, 'lower') and parent.can_reach2(node, ['child', 'higher']):
                        reconstruct_list.append(parent)
                for reconstruct in reconstruct_list:
                    reconstruct.remove_edge(node, 'lower')
                    higher.remove_edge(node, 'higher')
                    higher.add_edge(node, 'new')
    
    return graph


def draw_graph(graph):
    f = plt.figure(figsize=(GRAPH_WIDTH, GRAPH_WIDTH))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.MultiDiGraph()

    for i, node in enumerate(graph.get_node_list()):
        DG.add_node(node.name, name=node.name)

    for i, node in enumerate(graph.get_node_list()):
        for edge_node, edge_type in node.get_edges():
            DG.add_edge(node.name, edge_node.name, edge_type=edge_type)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)

    try:
        # pos = nx.shell_layout(DG)
        pos = hierarchy_pos_3(DG, 'done')
        nx.draw_networkx_nodes(DG, pos=pos)
    except Exception as e:
        print(e)
        # pos = nx.kamada_kawai_layout(DG)
        # pos = nx.spiral_layout(DG)
        pos = nx.random_layout(DG)
        nx.draw_networkx_nodes(DG, pos=pos)
    

    for edge_type, style, color in EDGE_STYLES:
        edges = [(u, v) for (u, v, d) in edgelist if d["edge_type"] == edge_type]
        nx.draw_networkx_edges(DG, pos=pos, edgelist=edges, style=style, edge_color=color, connectionstyle='arc3, rad={}'.format(random.uniform(0.05, 0.2)))
    
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
GRAPH_WIDTH = 8
FONT_SIZE = 8
EDGE_COLOR = "green"

CHILD = True

EDGE_STYLES = [
    ('child', 'solid', 'red'), 
    ('lower', 'dashed', 'green'), 
    ('higher', 'dashed', 'blue'),
    ('new', 'dashed', 'black')
    ]

# plot_list = ["13-1", "17-2", "09-1"]
# plot_list = ["07-1", "13-1", "15-2"]
# plot_list = ["07-1", "13-1", "15-2", "13-1", "17-2", "09-1"]

# plot_list = ['03-1', '07-1', '25-2']
# plot_list = ['16-2', '19-1', '10-2']
# plot_list = ['05-1']
# plot_list = ['05-1', '17-1']
# plot_list = ['17-1']

# plot_list = ['08-2', '18-1', '03-1']
# plot_list = ['08-2', '20-1', '06-1']

# plot_list = ['10-1', '11-2', '13-1', '15-1', '23-2', '08-2', '05-2', '11-1', '24-2', '08-1', '18-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '23-1', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '16-1', '24-1', '21-1', '27-1', '22-1']
# plot_list = ['10-1', '21-1', '26-2', '24-2']

# plot_list = ['10-1', '11-2', '13-1', '15-1', '23-2', '08-2', '05-2', '11-1', '24-2', '08-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '16-1', '24-1', '21-1', '27-1', '22-1']
# plot_list = ['12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '16-1', '24-1', '21-1', '27-1', '22-1']
# plot_list = ['12-2', '21-1']
# plot_list = ['12-2', '18-1']

plot_list = ["{:02}-{}".format(i, j) for i in range(1,28) for j in [1, 2]]
random.shuffle(plot_list)
# plot_list = plot_list[:30]

# individual_graph.main(plot_list)

print(plot_list)

all_action_list = []
for idx, plot_file in enumerate(plot_list):
    all_action_list.append(get_action_list("data/50salads/labels/{}-activityAnnotation.txt".format(plot_file)))

graph_object = construct_graph(all_action_list)
graph_object = reconstruct_graph(graph_object)
draw_graph(graph_object)
