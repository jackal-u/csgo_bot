import keyboard
import win32gui

from api import api
from map import map_grid
from route import main as route
import time, cv2
import random
from route import AstarSolver, RRTSolver,BiRRTSolver
import numpy as np
def find_nearst_pos(handle, bit_map, dx, dy, point1, custome = False):
    """
    与point1的相对位置 对dx dy 取余数，得到当前index
    当前index为中心的8个点，取最近的非障碍点为最终位置
    :param handle: API
    :param dx:
    :param dy:
    :param point1: [x, y , [index_x,index_y]]
    :return: i_r, i_c
    """
    if not custome:
        # 没有说明 默认返回当前玩家位置
        pos = handle.get_current_position()
        i_c = int((pos[0] - point1[0]) // dx + point1[2][1] + 1)
        i_r = int((pos[1] - point1[1]) // dy + point1[2][0] + 1)
        pos = find_kids(((-1, -1), (i_r, i_c)), [], bit_map,[])[1]
        if int(bit_map[(i_r, i_c, 0)]) == 0:
            print("NULL POSITION")
        return int(pos[1][0]), int(pos[1][1])
    else:
        # 说明了目标位置，则找寻符合要求的最近点
        pos = custome
        i_c = int((pos[0] - point1[0]) // dx + point1[2][1] + 1)
        i_r = int((pos[1] - point1[1]) // dy + point1[2][0] + 1)
        pos = find_kids(((-1, -1), (i_r, i_c)), [], bit_map, [])[1]
        if int(bit_map[(i_r, i_c, 0)]) == 0:
            print("NULL POSITION")
        return int(pos[1][0]), int(pos[1][1])

def find_kids(current_node: tuple, visited_nodes_pos: set, m: np.array, explored_nodes_pos: set) -> list:
    walk_ways = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    random.shuffle(walk_ways)
    kids = [(current_node, (current_node[1][0] + move[0], current_node[1][1] + move[1])) for move in
            walk_ways]
    f_kids = []
    for each in kids:
        try:
            obstacle = int(m[(each[1][0], each[1][1], 0)])
        except:
            continue
        if each[1] in visited_nodes_pos or obstacle == 0:
            continue
        if each[1] in explored_nodes_pos:
            continue
        f_kids.append((current_node, each[1]))
    return f_kids

def get_nearest_way_point(way_points: list, cur: tuple):
    print("get_nearest_way_point")
    dis = [manhattan(cur, point) for point in way_points]
    print("dis", dis)
    print("way_points", way_points)
    print("give", way_points[dis.index(min(dis))], dis.index(min(dis)))
    return way_points[dis.index(min(dis))], dis.index(min(dis))

def manhattan(pos1: tuple, pos2: tuple) -> float:
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])