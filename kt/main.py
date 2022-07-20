import networkx as nx
import matplotlib.pyplot as plt
import math
import numpy as np
import random
import copy
import json

from graph import *
import runner

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


def construct_graph(ACTIONS, EDGES):
    graph = Graph()
    for action in ACTIONS:
        cur_node = Node(action)
        graph.add_node(cur_node)

    for f_n, t_n, edge_type in EDGES:
        f_node = graph.get_node(f_n)
        t_node = graph.get_node(t_n)
        f_node.add_edge(t_node, edge_type)

    return graph


def draw_graph(graph, POS):
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
    
    for optional, shape in NODE_SHAPES:
        nodes = [n for (n, d) in nodelist if d["is_optional"] == optional]
        node_color = [STATE_COLORS[graph.get_node(n).state] for n in nodes]
        nx.draw_networkx_nodes(DG, pos=POS, nodelist=nodes, node_shape=shape, node_color=node_color)

    for edge_type, style, color in EDGE_STYLES:
        edges = [(u, v) for (u, v, d) in edgelist if d["edge_type"] == edge_type]
        nx.draw_networkx_edges(DG, pos=POS, edgelist=edges, style=style, edge_color=color, connectionstyle='arc3, rad={}'.format(0.05)) # random.uniform(0.05, 0.2)
    
    labels = nx.get_node_attributes(DG, 'name')
    description = nx.draw_networkx_labels(DG, pos=POS, labels=labels, font_size=FONT_SIZE)
    for node, t in description.items():
        t.set_rotation(LABEL_ROTATION)
    plt.box(False)

    plt.savefig("graphs_KT.png")

if __name__ == "__main__":
    METADATA = json.load(open('metadata.json'))

    graph_object = construct_graph(METADATA['ACTIONS'], METADATA['EDGES'])

    draw_graph(graph_object, METADATA['POS'])

    # To test with user inputted actions
    gr = runner.GraphRunner(graph_object)
    gr.run()
