import networkx as nx
import matplotlib.pyplot as plt
import math

high_level_nodes = ["cut_and_mix_ingredients", "prepare_dressing", "serve_salad"]
all_nodes = ["cut_and_mix_ingredients","peel_cucumber_prep","peel_cucumber_core","peel_cucumber_post",
"cut_cucumber_prep", "cut_cucumber_core", "cut_cucumber_post", "place_cucumber_into_bowl_prep", "place_cucumber_into_bowl_core", "place_cucumber_into_bowl_post",
"cut_tomato_prep", "cut_tomato_core", "cut_tomato_post", "place_tomato_into_bowl_prep", "place_tomato_into_bowl_core", "place_tomato_into_bowl_post",
"cut_cheese_prep", "cut_cheese_core", "cut_cheese_post", "place_cheese_into_bowl_prep", "place_cheese_into_bowl_core", "place_cheese_into_bowl_post",
"cut_lettuce_prep", "cut_lettuce_core", "cut_lettuce_post", "place_lettuce_into_bowl_prep", "place_lettuce_into_bowl_core", "place_lettuce_into_bowl_post",
"mix_ingredients_prep", "mix_ingredients_core", "mix_ingredients_post", "add_oil_prep", "add_oil_core", "add_oil_post", "add_vinegar_prep", "add_vinegar_core", "add_vinegar_post",
"add_salt_prep", "add_salt_core", "add_salt_post", "add_pepper_prep", "add_pepper_core", "add_pepper_post", "mix_dressing_prep", "mix_dressing_core", "mix_dressing_post",
"serve_salad_onto_plate_prep", "serve_salad_onto_plate_core", "serve_salad_onto_plate_post", "add_dressing_prep", "add_dressing_core", "add_dressing_post"]

def get_node_list(annotation_file):
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

def get_node_pos(i, node_count):
    x = i % GRAPH_WIDTH
    y = i // GRAPH_WIDTH + node_count // GRAPH_WIDTH
    if (i // GRAPH_WIDTH) % 2 == 1:
        x = GRAPH_WIDTH - x - 1
    return (x, -y*2)

def draw_graph(DG, idx, plot_file, node_list):
    global node_count, node_color

    for i, name in enumerate(node_list):
        if i == 0:
            name = "{}\n\n{}\n\n".format(plot_file, name)
        DG.add_node("{}_{}".format(idx, i), name=name, pos=get_node_pos(i, node_count))
        if name in HIGHLIGHT_NODE.keys():
            node_color.append(HIGHLIGHT_NODE[name])
        else:
            node_color.append('tab:blue')

    for i in range(len(node_list)-1):
        DG.add_edge("{}_{}".format(idx, i+1), "{}_{}".format(idx, i))

    node_count += len(node_list)
    node_count = GRAPH_WIDTH * math.ceil(node_count/GRAPH_WIDTH)

'''
Hyper-parameters
'''
LABEL_ROTATION = 30
GRAPH_WIDTH = 15
FONT_SIZE = 8
# HIGHLIGHT_NODE = {}
HIGHLIGHT_NODE = {'mix_ingredients': 'red', 'add_dressing': 'green', 'place_lettuce_into_bowl': 'black'}
# HIGHLIGHT_NODE = {'place_cucumber_into_bowl': 'red', 'cut_cucumber': 'green'}
# HIGHLIGHT_NODE = {'mix_dressing': 'red', 'add_salt': 'green'}
node_count = 0
node_color = []
plot_list = ["01-1", "02-1", "03-1"]

def main(plot_list):
    f = plt.figure(figsize=(GRAPH_WIDTH, int(GRAPH_WIDTH/5*len(plot_list))))
    r = f.canvas.get_renderer()
    plt.axis('equal')

    DG = nx.DiGraph()

    for idx, plot_file in enumerate(plot_list):
        node_list = get_node_list("data/50salads/labels/{}-activityAnnotation.txt".format(plot_file))
        draw_graph(DG, idx, plot_file, node_list)

    labels = nx.get_node_attributes(DG, 'name') 
    pos = nx.get_node_attributes(DG, 'pos') 
    nx.draw(DG, pos=pos, node_color=node_color)
    description = nx.draw_networkx_labels(DG, pos=pos, labels=labels, font_size=FONT_SIZE)
    for node, t in description.items():
        t.set_rotation(LABEL_ROTATION)

    plt.savefig("multi_graphs.png")

if __name__ == "__main__":
    main(plot_list)