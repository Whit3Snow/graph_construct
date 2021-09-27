
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


# plot_list = ["{:02}-{}".format(i, j) for i in range(1,28) for j in [1, 2]]
# plot_list = ['04-2', '16-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '24-1', '21-1', '27-1', '22-1']
plot_list = ['10-1', '11-2', '13-1', '15-1', '23-2', '08-2', '05-2', '11-1', '24-2', '08-1', '18-1', '12-2', '07-2', '07-1', '13-2', '06-2', '16-2', '23-1', '12-1', '11-1', '26-2', '04-1', '26-1', '14-2', '03-1', '16-1', '24-1', '21-1', '27-1', '22-1']

# target_actions = ['add_oil', 'add_vinegar', 'add_pepper', 'add_salt']
target_actions = ['mix_dressing']

found_list = []
for idx, plot_file in enumerate(plot_list):
    all_actions = get_action_list("data/50salads/labels/{}-activityAnnotation.txt".format(plot_file))
    for action in target_actions:
        if action not in all_actions:
            found_list.append(plot_file)
            break

print(found_list)