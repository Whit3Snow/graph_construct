import networkx as nx
import numpy as np
import random

# From https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3/29597209#29597209

def hierarchy_pos_1(G, root='end', width=5., vert_gap=2., vert_loc=0, xcenter=5):
    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    def hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter, pos=None, parent=None, done=[]):
        if pos is None:
            pos = {root:(xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        rem_children = remaining_children(children, done)
        if len(rem_children) != 0:
            dx = width/len(rem_children) 
            nextx = xcenter - width/2 - dx/2
            for child in rem_children:
                nextx += dx
                done.append(child)
                pos = hierarchy_pos(G, child, width=width, vert_gap=1, 
                                    vert_loc=vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent=root, done=done)
        return pos

    def remaining_children(children, done):
        return [c for c in children if c not in done]

    return hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def hierarchy_pos_2(G, root='end', levels=None, width=1., height=1.):
    def make_levels(levels, node, currentLevel=0, parent=None, done=[]):
        if not currentLevel in levels:
            levels[currentLevel] = {"total" : 0, "current" : 0}
        levels[currentLevel]["total"] += 1
        neighbors = list(G.neighbors(node))
        rem_neighbors = remaining_neighbors(neighbors, done)
        for neighbor in rem_neighbors:
            if not neighbor == parent:
                done.append(neighbor)
                levels =  make_levels(levels, neighbor, currentLevel+1, node, done)
        return levels

    def make_pos(pos, node, currentLevel=0, parent=None, vert_loc=0, done=[]):
        dx = 1/levels[currentLevel]["total"]
        left = dx/2
        pos[node] = ((left + dx*levels[currentLevel]["current"])*width, vert_loc)
        levels[currentLevel]["current"] += 1
        neighbors = list(G.neighbors(node))
        rem_neighbors = remaining_neighbors(neighbors, done)
        for neighbor in rem_neighbors:
            if not neighbor == parent:
                done.append(neighbor)
                pos = make_pos(pos, neighbor, currentLevel+1, node, vert_loc-vert_gap)
        return pos

    def remaining_neighbors(neighbors, done):
        return [n for n in neighbors if n not in done]

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    if levels is None:
        levels = make_levels({}, root)
    else:
        levels = {l:{"total": levels[l], "current": 0} for l in levels}

    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({}, root)


def hierarchy_pos_3(G, root='end', levels=None, width=1., height=1.):
    def make_levels(levels, node, currentLevel=0, parent=None, done=[]):
        if not currentLevel in levels:
            levels[currentLevel] = {"total" : 0, "current" : 0}
        levels[currentLevel]["total"] += 1
        neighbors = list(G.neighbors(node))
        neighbors = sorted(neighbors)
        rem_neighbors = remaining_neighbors(neighbors, done)
        for neighbor in rem_neighbors:
            if neighbor != parent and neighbor not in done:
                done.append(neighbor)
                if [n for n in rem_neighbors if (n != neighbor) and (neighbor in list(G.neighbors(n)))]:
                    newLevel = 2
                else:
                    newLevel = 1
                levels, done =  make_levels(levels, neighbor, currentLevel+newLevel, node, done)
        return levels, done

    def make_pos(pos, node, currentLevel=0, parent=None, vert_loc=0, done=[]):
        dx = 1/levels[currentLevel]["total"]
        left = dx/2
        pos[node] = ((left + dx*levels[currentLevel]["current"])*width, vert_loc)
        levels[currentLevel]["current"] += 1
        neighbors = list(G.neighbors(node))
        neighbors = sorted(neighbors)
        rem_neighbors = remaining_neighbors(neighbors, done)
        for neighbor in rem_neighbors:
            if neighbor != parent and neighbor not in done:
                done.append(neighbor)
                if [n for n in rem_neighbors if (n != neighbor) and (neighbor in list(G.neighbors(n)))]:
                    newLevel = 2
                else:
                    newLevel = 1
                pos, done = make_pos(pos, neighbor, currentLevel+newLevel, node, vert_loc-vert_gap*newLevel, done)
        return pos, done

    def remaining_neighbors(neighbors, done):
        return [n for n in neighbors if n not in done]

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    if levels is None:
        levels, _ = make_levels({}, root)
    else:
        levels = {l:{"total": levels[l], "current": 0} for l in levels}

    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({}, root)[0]


def hierarchy_pos_4(G, root='end'):

    def remaining_neighbors(neighbors):
        return [n for n in neighbors if n not in list(done.keys())]
    
    node_list = [root]
    done = {}
    done[root] = 0
    level = {}
    level[0] = [1, 0]

    for node in node_list:
        cur_level = done[node]
        child_nodes = list(G.neighbors(node))
        child_nodes = sorted(child_nodes, key=lambda x : -len(list(G.neighbors(x))))
        cur_child_cnt = -1
        cur_child_level = cur_level
        for child in remaining_neighbors(child_nodes):
            child_cnt = len(list(G.neighbors(child)))
            if cur_child_cnt < 0 or cur_child_cnt != child_cnt:
                cur_child_cnt = child_cnt
                cur_child_level += 1
                if cur_child_level not in level:
                    level[cur_child_level] = [0, 0]
            done[child] = cur_child_level
            level[cur_child_level][0] += 1
            node_list.append(child)

    max_level_cnt = max(list(level.values()))[0]
    pos = {}
    for node in done:
        y = done[node]
        level_cnt, idx = level[y]
        if level_cnt == 1:
            x = 0
        else:
            step = max_level_cnt/(level_cnt-1)
            start = -max_level_cnt/2
            end = max_level_cnt/2+1
            float_range_array = list(np.arange(start, end, step))
            x = float_range_array[idx]
        level[y][1] += 1
        pos[node] = (x, -y*max_level_cnt/4)
    return pos


def hierarchy_pos_50salads(G):
    pos = {}
    pos['end'] = (0, 0)

    pos['add_dressing'] = (-1.25, -1)
    pos['serve_salad_onto_plate'] =  (1.7, -1)

    pos['mix_dressing'] = (-1.25, -2)
    pos['mix_ingredients'] = (1.7, -2)
    
    pos['add_salt'] = (-2, -3)
    pos['add_vinegar'] = (-1.6, -3.6)
    pos['add_oil'] = (-0.9, -3.6)
    pos['add_pepper'] = (-0.5, -3)

    pos['place_lettuce_into_bowl'] = (0.6, -3)
    pos['cut_lettuce'] = (0.6, -4)

    pos['place_cheese_into_bowl'] = (1.4, -3)
    pos['cut_cheese'] = (1.4, -4)

    pos['place_tomato_into_bowl'] = (2.2, -3)
    pos['cut_tomato'] = (2.2, -4)

    pos['place_cucumber_into_bowl'] = (3.0, -3)
    pos['cut_cucumber'] = (3.0, -4)
    pos['peel_cucumber'] = (2.6, -5)

    return pos


def hierarchy_pos_50salads_hard(G):
    pos = {}
    pos['end'] = (0, 0)

    pos['add_dressing'] = (-1.25, -1)
    pos['serve_salad_onto_plate'] =  (1.7, -1)

    pos['mix_dressing'] = (-1.25, -2)
    pos['mix_ingredients'] = (1.7, -2)
    pos['ve'] = (1.7, -2.8)
    
    pos['add_salt'] = (-2, -3)
    pos['add_vinegar'] = (-1.6, -3.6)
    pos['add_oil'] = (-0.9, -3.6)
    pos['add_pepper'] = (-0.5, -3)

    pos['place_lettuce_into_bowl'] = (0.6, -3.6)
    pos['cut_lettuce'] = (0.6, -4.4)

    pos['place_cheese_into_bowl'] = (1.4, -3.6)
    pos['cut_cheese'] = (1.4, -4.4)

    pos['place_tomato_into_bowl'] = (2.2, -3.6)
    pos['cut_tomato'] = (2.2, -4.4)

    pos['place_cucumber_into_bowl'] = (3.0, -3.6)
    pos['cut_cucumber'] = (3.0, -4.4)
    pos['peel_cucumber'] = (2.6, -5.2)

    return pos