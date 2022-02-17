from mazelib import Maze
from mazelib.generate.Prims import Prims
import queue, copy
import numpy as np
from map import map_grid

# is available
def is_pos_available(new_pos: tuple, m: np.array, start: tuple) -> bool:
    """
    check if the last position in trajectory x was valid
    """
    if not new_pos:  # if null
        # print("null")
        return False
    try:
        if int(m[new_pos[0], new_pos[1], 0]) == 0:  # if barrier
            # print("barrier")
            return False
        if new_pos in [start]:  # if end or start
            # print("start")
            return False
        # print("true")
        return True
    except:
        # print("except")
        return False  # if out of bound


def is_x_available(x: list) -> bool:
    """
    check if x trajectory x was valid (repeats, init)
    """
    if not x:  # if null
        return False
    if len(set(x)) != len(x):  # if x has repeat
        return False
    return True


# move
def add(x: list, act: tuple) -> tuple:
    return x[-1][0] + act[0], x[-1][1] + act[1]


# is_continue
def is_continue(q: queue, end: tuple) -> bool:
    """
    continue if no available
    """
    for each in list(q.queue):
        if end in each:
            q.empty()
            q.put(each)
            return False
    if len(q.queue) == 0:
        print("NO SOLUTION")
    return True

start = (47, 101)
end = (41, 73)
map = map_grid.Map("de_cache")
bit_map = map.bit_map

def bfs_find_route(bit_map: np.array, start:tuple, end:tuple)->list:
    q = queue.Queue()
    q.put([start])
    while is_continue(q, end):
        x = q.get()
        print("{} is popped, cur_queue {} ".format(x, q.queue))
        if x[-1] == end:
            q.put(x)
            continue
        for movement in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_pos = add(x, movement)
            new_x = copy.deepcopy(x)

            if is_pos_available(new_pos, bit_map, start):
                new_x.append(new_pos)
            else:
                continue
            if is_x_available(new_x) and new_x not in list(q.queue):  # repeat route will be removed       #
                # print("{} is put in queue".format(new_x))
                q.put(new_x)
        print(len(q.queue), q.queue)
        print("moved")

    return q.get()

out = bfs_find_route(bit_map, start, end)
print("out:", out)



