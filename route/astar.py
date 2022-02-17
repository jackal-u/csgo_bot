from mazelib import Maze
from mazelib.generate.Prims import Prims
import queue, copy, operator
from scipy.spatial import distance
import matplotlib.pyplot as plt
from mazelib.solve.BacktrackingSolver import BacktrackingSolver

#
# init the maze
m = Maze(123)
m.generator = Prims(100, 110)
m.generate()
m.start = (1, 1)
m.end = (41, 47)
print(m)


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
    return distance.euclidean(pos1, pos2)


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
        print(li)
        return
    li.append(end[1])
    find_fin_path(li, end[0])


# from typing import Dict, Tuple, List
# def is_end_found(li: list, end: tuple)->bool:
#     """
#     当end出现在li中，停止
#     :param end: (father ,(int, int))
#     :param li: List[ (father ,(int, int)) ]
#     :return:
#     """
#     for each in li:
#         if each[1] == end[1]:
#             return True
#     return False

def find_kids(current_node: tuple, visited_nodes_pos: list, m: Maze) -> list:
    """
    按照上下左右，剔除非子节点，返回子节点
    :param current_node: (father, pos)
    :param visited_nodes_pos: [pos, pos, pos, pos]
    :param m:
    :return: kids = [kid], kid=(father, pos)
    """
    kids = [(current_node, (current_node[1][0] + move[0], current_node[1][1] + move[1])) for move in
            [(0, 1), (0, -1), (1, 0), (-1, 0)]]
    f_kids = []
    for each in kids:

        try:
            obstacle = m.grid[each[1]]
        except:   # 跳过非法索引
            continue
        if each[1] in visited_nodes_pos or obstacle == 1:
            # 删除 障碍 已访问节点
            continue
        f_kids.append((current_node, each[1]))
    # print("f_kids is",f_kids)
    return f_kids


def append_kids(q: queue.PriorityQueue, kids: list) -> None:
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
        # print(" append_kids h done", each[1])
        g = g_value_cost(each)
        val = (h + g, h, each)
        q.put(val)


q = queue.PriorityQueue()
# ele in q -> (father,  pos) with priority of F_value
# pos = (row, column)
start, end = (None, m.start), (None, m.end)
q.put((0 + heuristic(start[1], end[1]), heuristic(start[1], end[1]), start))
visited_nodes = []
visited_nodes_pos = []
# is_end_found(visited_nodes,end):
while True:
    out = q.get()[2]
    if out[1] == end[1]:  # operator.eq(out[1], end[1])
        break
    visited_nodes.append(out)
    visited_nodes_pos.append(out[1])
    kids = find_kids(out, visited_nodes_pos, m)  # kid = (father, (row, column))
    append_kids(q, kids)
    print(visited_nodes_pos)

fin_path = []
find_fin_path(fin_path, out)
fin_path.reverse()
print(fin_path)



m.solutions = [fin_path]
print(m)
