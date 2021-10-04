import networkx as nx
import matplotlib.pyplot as plt
import math
import numpy as np
from graph_1 import *
from pos import *
import random
import individual_graph
import copy

high_level_nodes = ["cut_and_mix_ingredients", "prepare_dressing", "serve_salad"]

def get_action_list(annotation_file):
    lines = open(annotation_file, 'r').read().splitlines()

    all_actions = []
    for line in lines:
        start_time, _, action_name = line.split(' ')
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


def construct_graph(all_action_list, action_set_path):
    graph = Graph()
    action_set = open(action_set_path, 'r').read().splitlines()
    for action in action_set:
        cur_node = Node(action)
        graph.add_node(cur_node)

    for num, action_list in enumerate(all_action_list):
        missing_nodes = [graph.get_node(name) for name in list(set(action_set)-set(action_list))]
        for idx, name in enumerate(action_list):
            cur_node = graph.get_node(name)

            # Lower nodes
            if cur_node.get_lowers() == None:
                cur_node.empty_lowers()
                for lower_name in action_list[:idx]:
                    lower_node = graph.get_node(lower_name)
                    if lower_node not in cur_node.get_lowers():
                        cur_node.add_lower(lower_node)
            else:
                updated_lowers = [lower_node for lower_node in cur_node.get_lowers() if lower_node.name in action_list[:idx]]
                cur_node.lower_nodes = updated_lowers
                # removed_lowers = list(set(cur_node.lower_nodes)-set(updated_lowers))
                # cur_node.lower_nodes = updated_lowers + [lower_node for lower_node in removed_lowers if lower_node in missing_nodes]
                
            # Higher nodes
            if cur_node.get_highers() == None:
                cur_node.empty_highers()
                for higher_name in action_list[idx+1:]:
                    higher_node = graph.get_node(higher_name)
                    if higher_node not in cur_node.get_highers():
                        cur_node.add_higher(higher_node)
            else:
                updated_highers = [higher_node for higher_node in cur_node.get_highers() if higher_node.name in action_list[idx+1:]]
                # cur_node.higher_nodes = updated_highers
                removed_highers = list(set(cur_node.higher_nodes)-set(updated_highers))
                cur_node.higher_nodes = updated_highers + [higher_node for higher_node in removed_highers if higher_node in missing_nodes]
                
            # After nodes
            for after_name in action_list[:idx]:
                after_node = graph.get_node(after_name)
                if after_node not in cur_node.get_afters():
                    cur_node.add_after(after_node)

        # Missing nodes in the first sequence
        if num == 0 and len(missing_nodes) > 0:
            existing_nodes = [graph.get_node(name) for name in list(set(action_list))]
            for e_node in existing_nodes:
                for m_node in missing_nodes:
                    # e_node.add_lower(m_node)
                    e_node.add_higher(m_node)

    return graph


def reconstruct_graph(graph):
    for i, node in enumerate(graph.get_node_list()):
        for l_node in node.get_lowers():
            if l_node not in node.get_edge_c_nodes():
                node.add_edge(l_node, 'lower')

    for i, node in enumerate(graph.get_node_list()):
        for h_node in node.get_highers():
            if h_node not in node.get_edge_c_nodes():
                h_node.add_edge(node, 'higher')

    # draw_graph(graph)
    # input()

    changed = True
    while changed:
        changed = False
        for i, node in enumerate(graph.get_node_list()):
            all_edges = node.get_edges().copy()
            j = 0
            while j < len(all_edges):
                _, c_node, c_edge_type = all_edges[j]
                if node.is_connected(c_node, visited_nodes=[], ignored_edges=[all_edges[j]], target_edge_types=[c_edge_type, 'lower']):
                    all_edges.remove(all_edges[j])
                    node.remove_edge(c_node, c_edge_type)
                    changed = True
                else:
                    j += 1

    # draw_graph(graph)
    # input()
    # graph1 = copy.deepcopy(graph)

    changed = True
    while changed:
        changed = False
        for i, node in enumerate(graph.get_node_list()):
            all_edges = node.get_edges().copy()
            j = 0
            while j < len(all_edges):
                removed = False
                _, c_node, c_edge_type = all_edges[j]

                # triangles
                if not removed:
                    if node.is_connected(c_node, visited_nodes=[], ignored_edges=[all_edges[j]], target_edge_types=[c_edge_type, 'lower', 'new']):
                        all_edges.remove(all_edges[j])
                        node.remove_edge(c_node, c_edge_type)
                        removed = True
                        changed = True

                # black edges
                if not removed:
                    is_black = len(node.get_parent_edges()) > 0
                    for _, p_node, p_edge_type in node.get_parent_edges():
                        if c_edge_type != 'higher' or p_edge_type == 'higher' or (p_node, c_node, 'lower') not in p_node.get_edges():
                            is_black = False
                            break
                    if is_black:
                        changed = True
                        for _, p_node, p_edge_type in node.get_parent_edges():
                            p_node.remove_edge(c_node, 'lower')
                        node.remove_edge(c_node, 'higher')
                        all_edges.pop(j)
                        node.add_edge(c_node, 'new')
                        all_edges.append((node, c_node, 'new'))
                        removed = True

                # optional nodes
                if not removed:
                    is_optional = len(node.get_parent_edges()) > 0
                    for _, p_node, p_edge_type in node.get_parent_edges():
                        if p_edge_type != 'higher':
                            is_optional = False
                            break
                        for rc_node in node.get_required_nodes():
                            if not p_node.requires(c_node):
                                is_optional = False
                                break
                    if is_optional:
                        changed = True
                        remove_list = node.get_parent_edges().copy()
                        node.set_optional()
                        for _, p_node, p_edge_type in remove_list:
                            p_node.remove_edge(node, 'higher')
                            p_node.add_edge(node, 'new')

                if not removed:
                    j += 1
    

    for i, node in enumerate(graph.get_node_list()):
        node_edges = node.get_edges().copy()
        for edge in node_edges:
            _, c_node, c_edge_type = edge
            if node not in c_node.get_afters():
                node.remove_edge(c_node, c_edge_type)
                node.add_edge(c_node, c_edge_type+"!")

    for i, node in enumerate(graph.get_node_list()):
        node.finalize_afters(graph.get_node_list())
        for a_node in node.get_afters():
            node.add_edge(a_node, 'after')

    # draw_graph(graph)
    # input()

    # draw_graph(graph1)
    # input()

    # draw_graph(graph)
    # while True:
    #     f_node = graph.get_node(input('from: '))
    #     t_node = graph.get_node(input('to: '))
    #     f_node.requires(t_node)

    return graph


def draw_graph(graph):
    f = plt.figure(figsize=(GRAPH_WIDTH, GRAPH_WIDTH))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.MultiDiGraph()

    node_color = []
    for i, node in enumerate(graph.get_node_list()):
        DG.add_node(node.name, name=node.name)
        color = 'tab:blue'
        if node.is_optional():
            color = 'tab:grey'
        node_color.append(color)

    for i, node in enumerate(graph.get_node_list()):
        for p_node, c_node, edge_type in node.get_edges():
            DG.add_edge(node.name, c_node.name, edge_type=edge_type)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)

    try:
        # pos = nx.shell_layout(DG)
        pos = hierarchy_pos_50salads(DG, 'done')
        nx.draw_networkx_nodes(DG, pos=pos, node_color=node_color)
    except Exception as e:
        print(e)
        # pos = nx.kamada_kawai_layout(DG)
        pos = nx.shell_layout(DG)
        nx.draw_networkx_nodes(DG, pos=pos)
    

    for edge_type, style, color in EDGE_STYLES:
        edges = [(u, v) for (u, v, d) in edgelist if d["edge_type"] == edge_type]
        nx.draw_networkx_edges(DG, pos=pos, edgelist=edges, style=style, edge_color=color, connectionstyle='arc3, rad={}'.format(0.05)) # random.uniform(0.05, 0.2)
    
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

EDGE_STYLES = [
    ('lower', 'dotted', 'red'), 
    ('higher', 'dotted', 'blue'),
    ('new', 'dotted', 'black'),
    ('lower!', 'solid', 'red'), 
    ('higher!', 'solid', 'blue'),
    ('new!', 'solid', 'black'),
    ('after', 'dotted', 'green')
    ]

# GOOD
# plot_list = ["13-1", "17-2", "09-1"]
# plot_list = ["07-1", "13-1", "15-2"]
# plot_list = ["07-1", "13-1", "15-2", "13-1", "17-2", "09-1"]

# NOT DONE
# plot_list = ['01-1', '04-2', '05-2']

# WORST
# plot_list = ['18-1', '26-2', '26-1']
# plot_list = ['26-2', '26-1', '18-1']
# plot_list = ['26-2', '26-1']

# WHY BLACK IS ADDED
# plot_list = ['26-2', '26-1', '04-2', '16-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '24-1', '21-1', '27-1', '22-1']

# plot_list = ['25-1', '20-1', '06-1', '20-2', '16-2', '01-1', '08-2', '01-2', '18-1', '10-1', '05-2', '07-2', '12-1', '02-2', '13-1', '23-2', '15-1', '09-1', '07-1', '22-1', '04-2', '14-1', '27-1', '02-1', '12-2', '13-2', '10-2', '17-2', '05-1', '27-2']
# plot_list = ['25-1', '20-1', '06-1', '20-2', '16-2', '08-2', '01-2', '18-1', '10-1', '05-2', '07-2', '12-1', '02-2', '13-1', '23-2', '15-1', '09-1', '07-1', '22-1', '04-2', '14-1', '27-1', '02-1', '12-2', '13-2', '10-2', '17-2', '05-1', '27-2']

# plot_list = ['09-1', '14-1', '20-2', '06-1', '21-1', '01-1', '24-2', '02-2', '08-1', '04-1', '25-1', '07-1', '03-2', '13-2', '11-2', '19-1', '15-2', '05-2', '15-1', '18-2']
plot_list = ['09-1', '14-1', '20-2', '06-1', '21-1', '24-2', '02-2', '08-1', '04-1', '25-1', '07-1', '03-2', '13-2', '11-2', '19-1', '15-2', '05-2', '15-1', '18-2']

# plot_list = ['01-1', '02-1', '17-2', '26-1', '03-2', '18-2', '01-2', '20-2', '09-2', '13-2', '25-1', '16-1', '22-2', '08-1', '15-1', '24-1', '20-1', '12-2', '21-1', '06-1']

# plot_list = ["{:02}-{}".format(i, j) for i in range(1,28) for j in [1, 2]]
# random.shuffle(plot_list)
# plot_list = plot_list[:20]

# individual_graph.main(plot_list)

print(plot_list)

all_action_list = []
for idx, plot_file in enumerate(plot_list):
    all_action_list.append(get_action_list("data/50salads/labels/{}-activityAnnotation.txt".format(plot_file)))

graph_object = construct_graph(all_action_list, "data/50salads/actions.txt")
graph_object = reconstruct_graph(graph_object)
draw_graph(graph_object)
