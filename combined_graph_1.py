import networkx as nx
import matplotlib.pyplot as plt
import math
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

# def construct_graph(activity_list, action_list_path):
#     graph = Graph()
#     all_actions = open(action_list_path, 'r').readlines()
#     all_actions = [action.strip() for action in all_actions]
#     for action in all_actions:
#         cur_node = Node(action)
#         graph.add_node(cur_node)

#     for activity in activity_list:
#         for idx, name in enumerate(activity):
#             cur_node = graph.get_node(name)
#             if not cur_node.is_activated():
#                 for lower_name in activity[:idx]:
#                     lower_node = graph.get_node(lower_name)
#                     if lower_node not in cur_node.get_lowers():
#                         cur_node.add_lower(lower_node)
#                 if idx > 0:
#                     child_node = graph.get_node(activity[idx-1])
#                     cur_node.add_child(child_node)
#             else:
#                 if idx == 0:
#                     cur_node.empty_childs()
#                     cur_node.empty_lowers()
#                 elif idx > 0:
#                     updated_lowers = [lower_node for lower_node in cur_node.get_lowers() if lower_node.name in activity[:idx]]
#                     cur_node.lower_nodes = updated_lowers
#                     updated_childs = [child_node for child_node in cur_node.get_childs() if child_node in cur_node.get_lowers()]
#                     cur_node.child_nodes = updated_childs
                    
#                     child_name = activity[idx-1]
#                     child_node = graph.get_node(child_name)
#                     if (child_node not in cur_node.get_childs()) and (child_node in cur_node.get_lowers()):
#                         cur_node.add_child(child_node)

#         for idx, name in enumerate(activity):
#             cur_node = graph.get_node(name)
#             if cur_node.get_highers() == None:
#                 cur_node.empty_highers()
#                 for higher_name in activity[idx+1:]:
#                     higher_node = graph.get_node(higher_name)
#                     if higher_node not in cur_node.get_highers():
#                         cur_node.add_higher(higher_node)
#             else:
#                 updated_highers = [higher_node for higher_node in cur_node.get_highers() if higher_node.name in activity[idx+1:]]
#                 cur_node.higher_nodes = updated_highers

#     return graph

def construct_graph(all_action_list, action_list_path):
    graph = Graph()
    for num, action_list in enumerate(all_action_list):
        for idx, name in enumerate(action_list):
            cur_node_list = graph.get_node(name)
            if len(cur_node_list) == 0 or num == 0:
                cur_node = Node(name)
                if idx > 0:
                    for lower_name in reversed(action_list[:idx]):
                        lower_node_list = graph.get_node(lower_name)
                        for lower_node in lower_node_list:
                            if lower_node.name not in [x.name for x in cur_node.get_lowers()]:
                                cur_node.add_lower(lower_node)
                    child_node_list = graph.get_node(action_list[idx-1])
                    cur_node.add_child(child_node_list[-1])
                graph.add_node(cur_node)
            else:
                for cur_node in cur_node_list:
                    if idx == 0:
                        cur_node.empty_childs()
                        cur_node.empty_lowers()
                    elif idx > 0:
                        updated_lowers = [lower_node for lower_node in cur_node.get_lowers() if lower_node.name in action_list[:idx]]
                        cur_node.lower_nodes = updated_lowers
                        updated_childs = [child_node for child_node in cur_node.get_childs() if child_node in cur_node.get_lowers()]
                        cur_node.child_nodes = updated_childs
                        
                        child_name = action_list[idx-1]
                        child_node_list = graph.get_node(child_name)
                        for child_node in child_node_list:
                            if (child_node not in cur_node.get_childs()) and (child_node in cur_node.get_lowers()):
                                cur_node.add_child(child_node)

        for idx, name in enumerate(action_list):
            cur_node_list = graph.get_node(name)
            for cur_node in cur_node_list:
                if cur_node.get_highers() == None:
                    cur_node.empty_highers()
                    for higher_name in action_list[idx+1:]:
                        higher_node_list = graph.get_node(higher_name)
                        for higher_node in higher_node_list:
                            if higher_node not in cur_node.get_highers():
                                cur_node.add_higher(higher_node)
                else:
                    updated_highers = [higher_node for higher_node in cur_node.get_highers() if higher_node.name in action_list[idx+1:]]
                    cur_node.higher_nodes = updated_highers

    return graph


def draw_graph(graph):
    f = plt.figure(figsize=(GRAPH_WIDTH, GRAPH_WIDTH))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.DiGraph()

    node_cnt = 0
    node_map = {}

    for i, node in enumerate(graph.get_node_list()):
        DG.add_node(node_cnt, name=node.name)
        node_map[node] = node_cnt
        node_cnt += 1

    for i, node in enumerate(graph.get_node_list()):
        for child in node.get_childs():
            style = '2' if node.num_childs() > 1 else '1'
            DG.add_edge(node_map[node], node_map[child], edge_type=style)
        
    #     for lower in node.get_lowers():
    #         print('+',lower)
    #         if lower not in node.get_childs():
    #             print('++',lower)
    #             if not node.can_reach(lower, []):
    #                 DG.add_edge(node_map[node], node_map[lower], edge_type='3')
    #                 child_node_list = graph.get_node(lower.name)
    #                 for child_node in child_node_list:
    #                     node.add_child(child_node)

    # for i, node in enumerate(graph.get_node_list(lambda x : x.num_highers())):
    #     for higher in node.get_highers():
    #         if node not in higher.get_childs():
    #             if not higher.can_reach(node, []):
    #                 DG.add_edge(node_map[higher], node_map[node], edge_type='4')
    #                 higher_node_list = graph.get_node(higher.name)
    #                 for higher_node in higher_node_list:
    #                     higher_node.add_child(node)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)

    try:
        pos = hierarchy_pos_1(DG, 'done')
        nx.draw_networkx_nodes(DG, pos=pos)
    except:
        # pos = nx.kamada_kawai_layout(DG)
        # pos = nx.spiral_layout(DG)
        # pos = nx.spectral_layout(DG)
        # pos = nx.spring_layout(DG)
        pos = nx.shell_layout(DG)
        # pos = nx.random_layout(DG)
        nx.draw_networkx_nodes(DG, pos=pos)
    

    for edge_type, style, color in [('1', 'solid', 'red'), ('2', 'dotted', 'red'), ('3', 'dashed', 'green'), ('4', 'dashed', 'blue')]:
        edges = [(u, v) for (u, v, d) in edgelist if d["edge_type"] == edge_type]
        nx.draw_networkx_edges(DG, pos=pos, edgelist=edges, style=style, edge_color=color)
    
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

# plot_list = ["13-1", "17-2", "09-1"]
# plot_list = ["07-1", "13-1", "15-2"]
# plot_list = ["07-1", "13-1", "15-2", "13-1", "17-2", "09-1"]

# plot_list = ['03-1', '07-1', '25-2']
# plot_list = ['16-2', '19-1', '10-2']
# plot_list = ['05-1', '17-1', '25-2']
# plot_list = ['17-1']
# plot_list = ['05-1']
plot_list = ['17-1', '05-1']
# plot_list = ['17-1', '25-2']


# plot_list = ["{:02}-{}".format(i, j) for i in range(1,28) for j in [1, 2]]
# random.shuffle(plot_list)
# plot_list = plot_list[:]

# individual_graph.main(plot_list)

print(plot_list)

all_action_list = []
for idx, plot_file in enumerate(plot_list):
    all_action_list.append(get_action_list("data/50salads/labels/{}-activityAnnotation.txt".format(plot_file)))

graph_object = construct_graph(all_action_list, "data/50salads/actions.txt")
draw_graph(graph_object)
