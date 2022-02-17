from mazelib import Maze
from mazelib.generate.Prims import Prims
import queue, copy
import matplotlib.pyplot as plt
from mazelib.solve.BacktrackingSolver import BacktrackingSolver

# init the maze
m = Maze(123)
m.generator = Prims(10, 11)
m.generate()
m.start = (1, 1)
m.end = (1, 5)

# is available
def is_pos_available(new_pos: tuple, m: Maze) -> bool:
    """
    check if the last position in trajectory x was valid
    """
    if not new_pos:  # if null
        # print("null")
        return False
    try:
        if m.grid[new_pos] == 1:  # if barrier
            # print("barrier")
            return False
        if new_pos in [m.start] :  # if end or start
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
def is_continue(q: queue, m: Maze) -> bool:
    """
    continue except all Xs has m.end
    """
    for each in list(q.queue):
        if m.end not in each:
            return True
    print("all routes is valid, queue: {}".format(list(q.queue)))
    if len(q.queue) == 0:
        print("NO SOLUTION")
    return False

def check_num_of_success(q: queue.Queue)->int:
    t=0
    for each in list(q.queue):
        if m.end in each:
            t+=1
    return t

# main loop
print(m)

q = queue.Queue()
q.put([m.start])
while is_continue(q, m):
    print("check_num_of_success, {}".format(check_num_of_success(q)))
    x = q.get()
    print("{} is popped, cur_queue {} ".format(x, q.queue))
    if x[-1] == m.end:
        q.put(x)
        continue
    for movement in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_pos = add(x, movement)
        new_x = copy.deepcopy(x)

        if is_pos_available(new_pos, m):
            new_x.append(new_pos)
        else:
            continue
        if is_x_available(new_x) and new_x not in list(q.queue):  # repeat route will be removed       #
            # print("{} is put in queue".format(new_x))
            q.put(new_x)

    print(len(q.queue), q.queue)
    print("moved")

m.solutions = q.queue
print(m)


