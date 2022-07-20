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
import dataloader_Breakfast

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

def construct_graph(all_action_list, action_set):
    graph = Graph()
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
                cur_node.update_lower_nodes(updated_lowers)
                
            # Higher nodes
            if cur_node.get_highers() == None:
                cur_node.empty_highers()
                for higher_name in action_list[idx+1:]:
                    higher_node = graph.get_node(higher_name)
                    if higher_node not in cur_node.get_highers():
                        cur_node.add_higher(higher_node)
            else:
                updated_highers = [higher_node for higher_node in cur_node.get_highers() if higher_node.name in action_list[idx+1:]]
                removed_highers = list(set(cur_node.higher_nodes)-set(updated_highers))
                updated_highers += [higher_node for higher_node in removed_highers if higher_node in missing_nodes]
                cur_node.update_higher_nodes(updated_highers)
                
            # After nodes
            for after_name in action_list[:idx]:
                after_node = graph.get_node(after_name)
                if after_node not in cur_node.get_afters():
                    cur_node.add_after(after_node)

        # Missing nodes in the first sequence
        if num == 0 and len(missing_nodes) > 0:
            existing_nodes = [graph.get_node(name) for name in list(set(action_list))]
            for e_node in existing_nodes:
                # if e_node.name == 'done':
                #     continue
                for m_node in missing_nodes:
                    # e_node.add_lower(m_node)
                    e_node.add_higher(m_node)

    return graph


def reconstruct_graph(graph):
    # Add all edges to lower nodes
    for i, node in enumerate(graph.get_node_list()):
        if node.get_lowers():
            for l_node in node.get_lowers():
                node.add_edge(l_node, 'lower')

    # Add all edges to higher nodes
    for i, node in enumerate(graph.get_node_list()):
        if node.get_highers():
            for h_node in node.get_highers():
                h_node.add_edge(node, 'higher')

    # Remove shortcut edges from triangles
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

    changed = True
    while changed:
        changed = False
        for i, node in enumerate(graph.get_node_list()):
            all_edges = node.get_edges().copy()
            j = 0
            while j < len(all_edges):
                removed = False
                _, c_node, c_edge_type = all_edges[j]

                # Remove shortcut edges from triangles
                if not removed:
                    if node.is_connected(c_node, visited_nodes=[], ignored_edges=[all_edges[j]], target_edge_types=[c_edge_type, 'lower', 'new']):
                        all_edges.remove(all_edges[j])
                        node.remove_edge(c_node, c_edge_type)
                        removed = True
                        changed = True

                # forced edges
                if not removed:
                    check_forced = len(node.get_parent_edges()) > 0
                    for _, p_node, p_edge_type in node.get_parent_edges():
                        if c_edge_type != 'higher' or p_edge_type == 'higher' or (p_node, c_node, 'lower') not in p_node.get_edges():
                            check_forced = False
                            break
                    if check_forced:
                        changed = True
                        for _, p_node, p_edge_type in node.get_parent_edges():
                            p_node.remove_edge(c_node, 'lower')
                        node.remove_edge(c_node, 'higher')
                        all_edges.pop(j)
                        node.add_edge(c_node, 'new')
                        all_edges.append((node, c_node, 'new'))
                        removed = True

                if not removed:
                    j += 1
            
            # optional nodes
            is_optional = len(node.get_parent_edges()) > 0
            for _, p_node, p_edge_type in node.get_parent_edges():
                if p_edge_type != 'higher':
                    is_optional = False
                    break
                for rc_node in node.get_required_nodes(): # CHECK
                    if not p_node.requires(rc_node):
                        is_optional = False
                        break
            if is_optional:
                changed = True
                remove_list = node.get_parent_edges().copy()
                node.set_optional()
                for _, p_node, p_edge_type in remove_list:
                    p_node.remove_edge(node, 'higher')
                    p_node.add_edge(node, 'new')

    for i, node in enumerate(graph.get_node_list()):
        node_edges = node.get_edges().copy()
        for edge in node_edges:
            _, c_node, c_edge_type = edge
            if node not in c_node.get_afters() and c_edge_type == 'new':
                node.remove_edge(c_node, 'new')
                node.add_edge(c_node, 'lower')

    # for i, node in enumerate(graph.get_node_list()):
    #     node.finalize_afters(graph.get_node_list())
    #     for a_node in node.get_afters():
    #         node.add_edge(a_node, 'after')

    # changed = True
    # while changed:
    #     changed = False
    #     for i, node in enumerate(graph.get_node_list()):
    #         all_edges = node.get_edges().copy()
    #         j = 0
    #         while j < len(all_edges):
    #             _, c_node, c_edge_type = all_edges[j]
    #             if c_edge_type == 'after' and node.is_connected(c_node, visited_nodes=[], ignored_edges=[all_edges[j]], target_edge_types=['after']):
    #                 all_edges.remove(all_edges[j])
    #                 node.remove_edge(c_node, c_edge_type)
    #                 changed = True
    #             else:
    #                 j += 1

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

    if dataset == '50salads':
        hierarchy_pos = hierarchy_pos_50salads
    elif 'Breakfast' in dataset:
        # hierarchy_pos = nx.shell_layout
        hierarchy_pos = hierarchy_pos_4

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
# dataset = 'Breakfast_coarse/sandwich'

if __name__ == "__main__":

    if dataset == '50salads':
        dataloader = dataloader_50salads.Dataloader(dataset)
    elif 'Breakfast' in dataset:
        dataloader = dataloader_Breakfast.Dataloader(dataset)

    all_action_list, data_list, action_set = dataloader.get_actions()

    individual_graph.main(data_list)

    graph_object = construct_graph(all_action_list, action_set)
    graph_object = reconstruct_graph(graph_object)

    draw_graph(graph_object)

    # To test with user inputted actions
    # gr = graph_runner.GraphRunner(graph_object)
    # gr.run()

    # To test videos used to create the graph
    # for action_list in all_action_list:
    #     gr = graph_runner.GraphRunner(graph_object, action_list)
    #     gr.run()
