import networkx as nx
import matplotlib.pyplot as plt
import math
import numpy as np
from graph_2 import *
from pos import *
import graph_runner
import random
import individual_graph
import copy

high_level_nodes = ["cut_and_mix_ingredients", "prepare_dressing", "serve_salad"]

freq = {'add_dressing':0, 'serve_salad_onto_plate':0, 'mix_dressing' : 0, 'mix_ingredients': 0,
            'add_salt':0, 'add_pepper': 0, 'place_lettuce_into_bowl':0, 'place_cheese_into_bowl':0, 'place_tomato_into_bowl': 0, 'place_cucumber_into_bowl' : 0,
            'add_vinegar':0, 'add_oil':0, 'cut_lettuce':0, 'cut_cheese':0, 'cut_tomato': 0, 'cut_cucumber': 0,
            'peel_cucumber':0 }

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
    thr = len(all_action_list) * 0.76
    graph = Graph()
    action_set = open(action_set_path, 'r').read().splitlines()
    for action in action_set: #해당 list에 존재하는 action추가 
        cur_node = Node(action)
        graph.add_node(cur_node)

    for num, action_list in enumerate(all_action_list):
        exist = []
        for idx, name in enumerate(action_list):
            rep = False
            for r_name in exist:
                if name == r_name:
                    rep = True

            if rep == True:
                continue
            cur_node = graph.get_node(name)
            # Lower nodes
            for lower_name in action_list[:idx]:
                exist.append(name)
                # cur_node.rep = True
                cur_node.add_lower(lower_name)

    # extract the lower nodes        
    for i, node in enumerate(graph.get_node_list()):
        for lower_name,value in node.lower_nums.items():
            if value > thr :
                lower_node = graph.get_node(lower_name)
                node.add_lower_list(lower_node)
    

    return graph
    

def reconstruct_graph(graph):
    # Add all edges to lower nodes
    for i, node in enumerate(graph.get_node_list()):
        for l_node in node.get_lowers():
            node.add_edge(l_node, 'lower')

        # print("lowers in reconstruct:",node.get_edges)

    print("first lower graph")

    draw_graph(graph)
    # input()

    changed = True
    while changed:
        changed = False
        for i, node in enumerate(graph.get_node_list()):
            all_edges = node.get_edges().copy()
            j = 0
            while j < len(all_edges):
                _, c_node, c_edge_type = all_edges[j]
                if node.is_connected(c_node, visited_nodes=[], ignored_edges=[all_edges[j]], target_edge_types=[c_edge_type]):
                    all_edges.remove(all_edges[j])
                    node.remove_edge(c_node, c_edge_type)
                    changed = True
                else:
                    j += 1

    

    return graph


def draw_graph(graph):
    f = plt.figure(figsize=(GRAPH_WIDTH, GRAPH_WIDTH))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.MultiDiGraph()

    for i, node in enumerate(graph.get_node_list()):
        node_name = node.name
        DG.add_node(node.name, name=node_name) 

    for i, node in enumerate(graph.get_node_list()):
        for p_node, c_node, edge_type in node.get_edges():
            DG.add_edge(node.name, c_node.name, edge_type=edge_type)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)

    pos = hierarchy_pos_50salads(DG, 'done')
    
    # for optional, shape in NODE_SHAPES:
    nodes = [n for (n, d) in nodelist]
        # node_color = [STATE_COLORS[graph.get_node(n).state] for n in nodes]
    nx.draw_networkx_nodes(DG, pos=pos, nodelist=nodes, node_shape='o', node_color='skyblue')

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
    ('lower', 'solid', 'red'), 
    ('higher', 'dashed', 'blue'),
    ('new', 'solid', 'black'),
    ('after', 'dotted', 'green')
]

NODE_SHAPES = [
    (False, 'o'), 
    (True, '^')
]

STATE_COLORS = [
    'tab:blue',
    'tab:green',
    'tab:red',
    'tab:grey'
]

if __name__ == "__main__":
    # GOOD
    # plot_list = ["13-1", "17-2", "09-1"]
    # plot_list = ["07-1", "13-1", "15-2"]
    # plot_list = ["07-1", "13-1", "15-2", "13-1", "17-2", "09-1"]

    # NOT DONE
    # plot_list = ['01-1', '04-2', '05-2']
    # plot_list = ['27-1', '06-2', '23-1', '19-1', '20-1', '25-2', '15-1', '01-1', '24-1', '12-1', '18-1', '01-2', '17-2', '04-2', '14-1', '25-1', '02-1', '15-2', '16-2', '03-2']
    # plot_list = ['22-2', '03-2', '14-2', '06-2', '23-1', '15-2', '04-2', '03-1', '21-2', '19-2', '14-1', '16-1', '07-1', '17-2', '20-2', '26-2', '09-1', '06-1', '21-1', '02-2']
    # plot_list = ['13-2', '09-2', '21-2', '27-1', '23-2', '03-1', '10-1', '13-1', '15-1', '02-1', '19-2', '19-1', '23-1', '05-1', '08-1', '06-2', '24-2', '04-2', '22-2', '05-2']

    # WORST
    # plot_list = ['18-1', '26-2', '26-1']
    # plot_list = ['26-2', '26-1', '18-1']
    # plot_list = ['26-2', '26-1']

    # WHY BLACK IS ADDED
    # plot_list = ['26-2', '26-1', '04-2', '16-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '24-1', '21-1', '27-1', '22-1']

    # plot_list = ['25-1', '20-1', '06-1', '20-2', '16-2', '01-1', '08-2', '01-2', '18-1', '10-1', '05-2', '07-2', '12-1', '02-2', '13-1', '23-2', '15-1', '09-1', '07-1', '22-1', '04-2', '14-1', '27-1', '02-1', '12-2', '13-2', '10-2', '17-2', '05-1', '27-2']
    # plot_list = ['25-1', '20-1', '06-1', '20-2', '16-2', '08-2', '01-2', '18-1', '10-1', '05-2', '07-2', '12-1', '02-2', '13-1', '23-2', '15-1', '09-1', '07-1', '22-1', '04-2', '14-1', '27-1', '02-1', '12-2', '13-2', '10-2', '17-2', '05-1', '27-2']

    # plot_list = ['09-1', '14-1', '20-2', '06-1', '21-1', '01-1', '24-2', '02-2', '08-1', '04-1', '25-1', '07-1', '03-2', '13-2', '11-2', '19-1', '15-2', '05-2', '15-1', '18-2']
    # plot_list = ['09-1', '14-1', '20-2', '06-1', '21-1', '24-2', '02-2', '08-1', '04-1', '25-1', '07-1', '03-2', '13-2', '11-2', '19-1', '15-2', '05-2', '15-1', '18-2']

    # plot_list = ['18-1', '23-1', '25-2', '04-1', '06-1', '11-1', '09-2', '24-1', '26-1', '02-2', '19-2', '05-1', '27-2', '15-1', '10-2', '08-2', '18-2', '21-2', '20-2', '12-2']
    # plot_list = ['01-1', '02-1', '17-2', '26-1', '03-2', '18-2', '01-2', '20-2', '09-2', '13-2', '25-1', '16-1', '22-2', '08-1', '15-1', '24-1', '20-1', '12-2', '21-1', '06-1']
    # plot_list = ['27-1', '13-2', '15-1', '27-2', '16-2', '08-1', '22-1', '06-1', '16-1', '03-2', '07-2', '05-2', '09-2', '23-1', '05-1', '08-2', '14-2', '24-2', '03-1', '18-1']
    # plot_list = ['09-1', '22-2', '25-1', '23-1', '08-1', '06-2', '10-2', '18-1', '21-2', '15-1', '01-2', '03-1', '04-2', '05-1', '16-1', '20-1', '17-2', '12-1', '14-2', '21-1']
    # plot_list = ['25-2', '03-2', '22-1', '12-2', '05-2', '27-1', '15-2', '10-1', '09-1', '12-1', '13-2', '04-2', '14-2', '18-1', '17-1', '08-1', '20-2', '19-2', '13-1', '21-2']
    # plot_list = ['09-1', '16-2', '07-2', '24-1', '06-1', '01-2', '09-2', '18-2', '20-1', '25-2', '16-1', '19-1', '10-2', '18-1', '04-2', '21-2', '26-1', '11-2', '25-1', '26-2']
    # plot_list = ['17-1', '17-2', '09-2', '03-1', '01-1', '08-2', '11-1', '15-2', '10-1', '26-2', '16-2', '22-1', '12-2', '20-1', '12-1', '19-2', '26-1', '02-1', '06-2', '04-1']

    plot_list = ["{:02}-{}".format(i, j) for i in range(1,28) for j in [1, 2]]
    random.shuffle(plot_list)
    # plot_list = plot_list[:20]

    # individual_graph.main(plot_list)

    print(plot_list)

    all_action_list = []
    for idx, plot_file in enumerate(plot_list):
        all_action_list.append(get_action_list("data/50salads/labels/{}-activityAnnotation.txt".format(plot_file)))

    graph_object = construct_graph(all_action_list, "data/50salads/actions.txt")
    graph_object = reconstruct_graph(graph_object)

    draw_graph(graph_object)

