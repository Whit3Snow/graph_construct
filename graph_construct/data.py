import networkx as nx
import matplotlib.pyplot as plt

high_level_nodes = ["cut_and_mix_ingredients", "prepare_dressing", "serve_salad"]

#f = open("C:/Users/wkdgy/Desktop/3학년 여름 개별연구/01-2-activityAnnotation.txt",'r')
f = open("C:/Users/wkdgy/Desktop/ann-ts/activityAnnotations/02-1-activityAnnotation.txt", 'r')

data = []
action_list = []

while True:

    line = f.readline()    
    if not line: break
    
    tokens = line.split(' ')
    if tokens[2][:-1] in high_level_nodes:
        continue
    action_list.append([tokens[0], tokens[2][:-1]])

action_list = sorted(action_list, key=lambda x : int(x[0]))

refined_action = []
for action in action_list:
    label = action[1]
    type = label.split('_')[-1]
    if type in ['core', 'prep', 'post']:
        label = "_".join(label.split('_')[:-1])
    if len(refined_action) == 0 or refined_action[-1] != label:
        refined_action.append(label) 

print(refined_action)
data = refined_action
    # print(line)
    # line = line

    # if line[-4:] == 'core' or 'prep' or 'post':
    #     line = line[:-5]
    
    # print(line)
    # data.append(line)

#print(data)
f.close()

"""
prep : 준비, 처음에 돌릴 때

"""

DG = nx.DiGraph()
node = ["cut_and_mix_ingredients","peel_cucumber_prep","peel_cucumber_core","peel_cucumber_post",
"cut_cucumber_prep", "cut_cucumber_core", "cut_cucumber_post", "place_cucumber_into_bowl_prep", "place_cucumber_into_bowl_core", "place_cucumber_into_bowl_post",
"cut_tomato_prep", "cut_tomato_core", "cut_tomato_post", "place_tomato_into_bowl_prep", "place_tomato_into_bowl_core", "place_tomato_into_bowl_post",
"cut_cheese_prep", "cut_cheese_core", "cut_cheese_post", "place_cheese_into_bowl_prep", "place_cheese_into_bowl_core", "place_cheese_into_bowl_post",
"cut_lettuce_prep", "cut_lettuce_core", "cut_lettuce_post", "place_lettuce_into_bowl_prep", "place_lettuce_into_bowl_core", "place_lettuce_into_bowl_post",
"mix_ingredients_prep", "mix_ingredients_core", "mix_ingredients_post", "add_oil_prep", "add_oil_core", "add_oil_post", "add_vinegar_prep", "add_vinegar_core", "add_vinegar_post",
"add_salt_prep", "add_salt_core", "add_salt_post", "add_pepper_prep", "add_pepper_core", "add_pepper_post", "mix_dressing_prep", "mix_dressing_core", "mix_dressing_post",
"serve_salad_onto_plate_prep", "serve_salad_onto_plate_core", "serve_salad_onto_plate_post", "add_dressing_prep", "add_dressing_core", "add_dressing_post"]

# for i in node:
#     DG.add_node(i)

for idx, i in enumerate(data):
    DG.add_node(idx, name=i)

for i in range(len(data)-1):
    # DG.add_edge(data[i], data[i+1])
    DG.add_edge(i, i+1)

label_dict = {}
for idx, i in enumerate(data):
    label_dict[idx] = i

nx.draw(DG, labels = label_dict, with_labels = True)
# nx.draw_networkx_labels(DG, data)
plt.show()
