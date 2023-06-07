import queue, copy, operator
import numpy as np
import random
from scipy.spatial import distance

class AstarSolver:
    def __init__(self):
        pass

    @staticmethod
    def manhattan(pos1: tuple, pos2: tuple) -> float:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @staticmethod
    def heuristic(pos1: tuple, pos2: tuple) -> float:
        if None in [pos1, pos2]:
            print("null position")
        if pos1 == pos2:
            return 0
        return AstarSolver.manhattan(pos1, pos2)

    @staticmethod
    def g_value_cost(ele: tuple) -> float:
        if ele[0] == (-1, -1):
            return 0
        return AstarSolver.manhattan(ele[0][1], ele[1]) + AstarSolver.g_value_cost(ele[0])

    @staticmethod
    def find_fin_path(li: list, end: tuple) -> None:
        if end[0] == (-1, -1):
            li.append(end[1])
            return
        li.append(end[1])
        AstarSolver.find_fin_path(li, end[0])

    @staticmethod
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

    @staticmethod
    def append_kids(q: queue.PriorityQueue, kids: list, end: tuple, explored_nodes_pos: set) -> None:
        for each in kids:
            h = AstarSolver.heuristic(each[1], end[1])
            g = AstarSolver.g_value_cost(each)
            val = (h + g, h + random.random(), each)
            q.put(val)
            explored_nodes_pos.add(each[1])

    def solve_maze_a_star(self, start: tuple, end: tuple, bitmap: np.array) -> list:
        q = queue.PriorityQueue()
        h = self.heuristic(start[1], end[1])
        q.put((0 + h, h, start))
        explored_nodes_pos = set()
        visited_nodes_pos = set()

        while True:
            out = q.get()[2]
            if out[1] == end[1]:
                break
            visited_nodes_pos.add(out[1])
            kids = self.find_kids(out, visited_nodes_pos, bitmap, explored_nodes_pos)
            self.append_kids(q, kids, end, explored_nodes_pos)

        fin_path = []
        self.find_fin_path(fin_path, out)
        fin_path.reverse()
        return fin_path