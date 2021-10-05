import networkx as nx
import matplotlib.pyplot as plt
import math
import numpy as np
from graph import *
from pos import *
import graph_runner
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
                for m_node in missing_nodes:
                    # e_node.add_lower(m_node)
                    e_node.add_higher(m_node)

    return graph


def reconstruct_graph(graph):
    # Add all edges to lower nodes
    for i, node in enumerate(graph.get_node_list()):
        for l_node in node.get_lowers():
            node.add_edge(l_node, 'lower')

    # Add all edges to higher nodes
    for i, node in enumerate(graph.get_node_list()):
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

    for i, node in enumerate(graph.get_node_list()):
        node.finalize_afters(graph.get_node_list())
        for a_node in node.get_afters():
            node.add_edge(a_node, 'after')

    changed = True
    while changed:
        changed = False
        for i, node in enumerate(graph.get_node_list()):
            all_edges = node.get_edges().copy()
            j = 0
            while j < len(all_edges):
                _, c_node, c_edge_type = all_edges[j]
                if c_edge_type == 'after' and node.is_connected(c_node, visited_nodes=[], ignored_edges=[all_edges[j]], target_edge_types=['after']):
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
        if node.executed:
            node_name = "X\n" + node_name
        DG.add_node(node.name, name=node_name, is_optional=node.is_optional())

    for i, node in enumerate(graph.get_node_list()):
        for p_node, c_node, edge_type in node.get_edges():
            DG.add_edge(node.name, c_node.name, edge_type=edge_type)

    nodelist = DG.nodes(data=True)
    edgelist = DG.edges(data=True)

    pos = hierarchy_pos_50salads(DG, 'done')
    
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
    plot_list = ['26-2', '26-1', '04-2', '16-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '24-1', '21-1', '27-1', '22-1']

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

    # To test with user inputted actions
    gr = graph_runner.GraphRunner(graph_object)
    gr.run()

    # To test videos used to create the graph
    # for action_list in all_action_list:
    #     gr = graph_runner.GraphRunner(graph_object, action_list)
    #     gr.run()
