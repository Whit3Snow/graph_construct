import networkx as nx
import matplotlib.pyplot as plt
import math
import numpy as np
import random
import copy

import individual_graph
from graph import *
from pos import *
import graph_runner
import dataloader_50salads

'''
Hyper-parameters
'''
LABEL_ROTATION = 10
GRAPH_WIDTH = 10
FONT_SIZE = 8
EDGE_COLOR = "green"

EDGE_STYLES = [
    ('lower', 'solid', 'red'), 
    ('higher', 'solid', 'blue'),
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

EDGE_LIST = [
    ('end', 'add_dressing', 'lower'),
    ('end', 'serve_salad_onto_plate', 'lower'),
    ('add_dressing', 'mix_dressing', 'lower'),
    ('mix_dressing', 'add_oil', 'higher'),
    ('mix_dressing', 'add_vinegar', 'higher'),
    ('mix_dressing', 'add_salt', 'higher'),
    ('mix_dressing', 'add_pepper', 'higher'),
    ('serve_salad_onto_plate', 'mix_ingredients', 'lower'),
    ('mix_ingredients', 'place_lettuce_into_bowl', 'higher'),
    ('mix_ingredients', 'place_cheese_into_bowl', 'higher'),
    ('mix_ingredients', 'place_tomato_into_bowl', 'higher'),
    ('mix_ingredients', 'place_cucumber_into_bowl', 'higher'),
    ('place_lettuce_into_bowl', 'cut_lettuce', 'lower'),
    ('place_cheese_into_bowl', 'cut_cheese', 'lower'),
    ('place_tomato_into_bowl', 'cut_tomato', 'lower'),
    ('place_cucumber_into_bowl', 'cut_cucumber', 'lower'),
    ('cut_cucumber', 'peel_cucumber', 'lower')
]

# EDGE_LIST = [
#     ('end', 'add_dressing', 'lower'),
#     ('end', 'serve_salad_onto_plate', 'lower'),
#     ('add_dressing', 'mix_dressing', 'lower'),
#     ('add_dressing', 've', 'lower'),
#     ('mix_dressing', 'add_oil', 'higher'),
#     ('mix_dressing', 'add_vinegar', 'higher'),
#     ('mix_dressing', 'add_salt', 'higher'),
#     ('mix_dressing', 'add_pepper', 'higher'),
#     ('serve_salad_onto_plate', 'mix_ingredients', 'lower'),
#     ('mix_ingredients', 've', 'lower'),
#     ('ve', 'place_lettuce_into_bowl', 'higher'),
#     ('ve', 'place_cheese_into_bowl', 'higher'),
#     ('ve', 'place_tomato_into_bowl', 'higher'),
#     ('ve', 'place_cucumber_into_bowl', 'higher'),
#     ('place_lettuce_into_bowl', 'cut_lettuce', 'lower'),
#     ('place_cheese_into_bowl', 'cut_cheese', 'lower'),
#     ('place_tomato_into_bowl', 'cut_tomato', 'lower'),
#     ('place_cucumber_into_bowl', 'cut_cucumber', 'lower'),
#     ('cut_cucumber', 'peel_cucumber', 'lower')
# ]

NODE_LIST = [
    ('peel_cucumber', False),
    ('cut_cucumber', False),
    ('place_cucumber_into_bowl', False),
    ('cut_tomato', False),
    ('place_tomato_into_bowl', False),
    ('cut_cheese', False),
    ('place_cheese_into_bowl', False),
    ('cut_lettuce', False),
    ('place_lettuce_into_bowl', False),
    ('mix_ingredients', False),
    # ('ve', False),
    ('add_oil', False),
    ('add_vinegar', False),
    ('add_salt', False),
    ('add_pepper', False),
    ('mix_dressing', True),
    ('serve_salad_onto_plate', False),
    ('add_dressing', True),
    ('end', False)
]

def construct_graph(all_action_list, action_set):
    graph = Graph()
    for action, optional in NODE_LIST:
        cur_node = Node(action)
        cur_node.optional = optional
        graph.add_node(cur_node)

    for f_n, t_n, edge_type in EDGE_LIST:
        f_node = graph.get_node(f_n)
        t_node = graph.get_node(t_n)
        f_node.add_edge(t_node, edge_type)

    return graph


def draw_graph(graph):
    f = plt.figure(figsize=(GRAPH_WIDTH, GRAPH_WIDTH))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.MultiDiGraph()

    for i, node in enumerate(graph.get_node_list()):
        node_name = node.name
        if node.executed:
            node_name = "X\n" + node_name
        DG.add_node(node.name, name=node_name, is_optional=node.is_optional())

    for i, node in enumerate(graph.get_node_list()):
        for p_node, c_node, edge_type in node.get_edges():
            DG.add_edge(node.name, c_node.name, edge_type=edge_type)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)

    hierarchy_pos = hierarchy_pos_50salads_hard

    pos = hierarchy_pos(DG)
    
    for optional, shape in NODE_SHAPES:
        nodes = [n for (n, d) in nodelist if d["is_optional"] == optional]
        node_color = [STATE_COLORS[graph.get_node(n).state] for n in nodes]
        nx.draw_networkx_nodes(DG, pos=pos, nodelist=nodes, node_shape=shape, node_color=node_color)

    for edge_type, style, color in EDGE_STYLES:
        edges = [(u, v) for (u, v, d) in edgelist if d["edge_type"] == edge_type]
        nx.draw_networkx_edges(DG, pos=pos, edgelist=edges, style=style, edge_color=color, connectionstyle='arc3, rad={}'.format(0.05)) # random.uniform(0.05, 0.2)
    
    labels = nx.get_node_attributes(DG, 'name')
    description = nx.draw_networkx_labels(DG, pos=pos, labels=labels, font_size=FONT_SIZE)
    for node, t in description.items():
        t.set_rotation(LABEL_ROTATION)
    plt.box(False)

    plt.savefig("graphs_{}.png".format(dataset.replace('/', '_')))


dataset = '50salads'

if __name__ == "__main__":

    dataloader = dataloader_50salads.Dataloader(dataset)

    all_action_list, data_list, action_set = dataloader.get_actions()

    # individual_graph.main(data_list)

    graph_object = construct_graph(all_action_list, action_set)

    draw_graph(graph_object)

    # To test with user inputted actions
    # gr = graph_runner.GraphRunner(graph_object)
    # gr.run()

    # To test videos used to create the graph
    # for action_list in all_action_list:
    #     gr = graph_runner.GraphRunner(graph_object, action_list)
    #     gr.run()
