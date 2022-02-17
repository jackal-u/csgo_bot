from mazelib import Maze
from mazelib.generate.Prims import Prims
import queue, copy, operator
from scipy.spatial import distance
import matplotlib.pyplot as plt
from mazelib.solve.BacktrackingSolver import BacktrackingSolver
import numpy as np
import random

def manhattan(pos1: tuple, pos2: tuple)->float:
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])


def heuristic(pos1: tuple, pos2: tuple) -> float:
    """
    简单根据位置计算欧氏距离
    :param pos1:
    :param pos2:
    :return:
    """
    if None in [pos1, pos2]:
        print("null position")
    if pos1 == pos2:
        return 0
    #print("pos1, pos2", pos1, pos2)
    return manhattan(pos1, pos2)


def g_value_cost(ele: tuple) -> float:
    """
    递归逆向遍历至起点，对路径进行加和
    :param ele: (father, pos), pos =(row, column)
    :return:
    """
    # print("ele:", ele)
    if ele[0] is None:
        return 0
    return distance.euclidean(ele[0][1], ele[1]) + g_value_cost(ele[0])


def find_fin_path(li: list, end: tuple) -> None:
    if end[0] is None:
        li.append(end[1])
        #print(li)
        return
    li.append(end[1])
    find_fin_path(li, end[0])


def find_kids(current_node: tuple, visited_nodes_pos: list, m: np.array) -> list:
    """
    按照上下左右，剔除非子节点，返回子节点
    :param current_node: (father, pos)
    :param visited_nodes_pos: [pos, pos, pos, pos]
    :param m:
    :return: kids = [kid], kid=(father, pos)
    """
    kids = [(current_node, (current_node[1][0] + move[0], current_node[1][1] + move[1])) for move in
            [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]]
    f_kids = []
    for each in kids:

        try:
            obstacle = int(m[(each[1][0], each[1][1], 0)])
        except:   # 跳过非法索引
            continue
        if each[1] in visited_nodes_pos or obstacle == 0:  # 0表示不可通行的障碍物
            # 删除 障碍 已访问节点
            continue
        f_kids.append((current_node, each[1]))
    # print("f_kids is",f_kids)
    return f_kids


def append_kids(q: queue.PriorityQueue, kids: list, end:tuple) -> None:
    """
    以 heuristic + G_value 为权值，把kids加入优先队列。
    :param q:
    :param kids:
    :return:
    """
    # print("kids", kids)
    for each in kids:
        # print("each before g_value", each)
        # print("end before g_value", end)
        h = heuristic(each[1], end[1])
        #print(" append_kids h done", each[1])
        g = g_value_cost(each)
        val = (h + g, h+random.random(), each)
        q.put(val)

import time
def solve_maze_a_star(start: tuple, end: tuple, bitmap:np.array)->list:
        q = queue.PriorityQueue()
        # ele in q -> (father,  pos) with priority of F_value
        # pos = (row, column)
        # start, end = (None, (1, 1)), (None, (1, 5))
        h = heuristic(start[1], end[1])
        print(" start h done")
        q.put((0 + h, h, start))
        visited_nodes = []
        visited_nodes_pos = []
        # is_end_found(visited_nodes,end):
        while True:
            out = q.get()[2]
            t0 = time.time()
            #print("OUT,", len(list(q.queue)), out)
            if out[1] == end[1]: #operator.eq(out[1], end[1])
                break
            visited_nodes.append(out)
            visited_nodes_pos.append(out[1])
            #t_append = time.time()
            # print("append list cost", t_append-t0)
            kids = find_kids(out, visited_nodes_pos, bitmap)  # kid = (father, (row, column))
            find_kids_time = time.time()
            # print("  find_kids cost ", find_kids_time - t_append)
            append_kids(q, kids, end)
            # print("append kids cost", time.time()-find_kids_time)
            # print("1 iteration cost", time.time() - t0)
        fin_path = []
        find_fin_path(fin_path, out)
        fin_path.reverse()
        print(fin_path)
        return fin_path


