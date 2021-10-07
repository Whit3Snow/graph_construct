import os
import random

class Dataloader():
    def __init__(self, dataset):
        self.dataset = dataset

    def get_actions(self):
        data_list = self.get_data_list()

        action_set = open("data/{}/actions.txt".format(self.dataset), 'r').read().splitlines()

        all_action_list = []
        for idx, data_file in enumerate(data_list):
            annotation_file = "data/{}/labels/{}".format(self.dataset, data_file)
            lines = open(annotation_file, 'r').read().splitlines()

            all_actions = []
            for line in lines:
                action_name = line.split()[-1]
                if action_name != "SIL" and action_name != "garbage":
                    all_actions.append(action_name)
            all_actions.append("done")
            
            all_action_list.append(all_actions)
        print(all_action_list)
        return all_action_list, data_list, action_set

    def get_data_list(self):
        data_list = os.listdir("data/{}/labels".format(self.dataset))
        random.shuffle(data_list)
        # data_list = data_list[:20]

        return data_list