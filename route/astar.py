import queue, copy, operator
import numpy as np
import random
import cv2
from typing import List, Tuple, ClassVar
from scipy.spatial import distance
from sklearn.neighbors import KDTree

from map import Map

class AstarSolver:
    def __init__(self, map_:Map):
        bit_map, dx, dy, point1 = map_.bit_map, map_.dx, map_.dy, map_.point1
        self.bitmap = bit_map
        bitmap_obstacles = np.squeeze(bit_map[:,:,0])
        # convert obstacles in bitmap to KDtrees
        self.train = np.argwhere(bitmap_obstacles==False)
        # false 代表障碍物 true代表可通行
        self.obstacles = KDTree(self.train)


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

    def obstacle_heuristic(self, ele:tuple, radius:int,scale:int):
        ele = np.expand_dims(np.array(ele), axis=0)
        distances, indices = self.obstacles.query(ele,k=1)
        o = max(radius - scale*distances[0][0], 0)
        return o


    @staticmethod
    def find_fin_path(li: list, end: tuple) -> None:
        if end[0] == (-1, -1):
            li.append(end[1])
            return
        li.append(end[1])
        AstarSolver.find_fin_path(li, end[0])


    def find_kids(self, current_node: tuple, visited_nodes_pos: set, explored_nodes_pos: set) -> list:
        m = self.bitmap
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

    def append_kids(self, q: queue.PriorityQueue, kids: list, end: tuple, explored_nodes_pos: set, radius:int,scale:int) -> None:
        for each in kids:
            h = self.heuristic(each[1], end[1])
            g = self.g_value_cost(each)
            o = self.obstacle_heuristic(ele=each[1], radius=radius,scale=scale)
            val = (h + g + o, h +o+ random.random(), each)
            q.put(val)
            explored_nodes_pos.add(each[1])

    def draw_routes(self, solution: List[Tuple[int, int]], bit_map: np.array, show:bool=True) -> np.array:
        ## get map
        img_np = bit_map[:, :, 0]
        way_points_np = np.zeros(img_np.shape)
        path_np = np.zeros(img_np.shape)

        ## draw waypoints
        # for each in self.way_points:
        #     way_points_np[each] = 250

        ## draw path
        for each in solution:
            path_np[each] = 100

        ## draw me
        # way_points_np[self.cur_pos] = 200
        img = np.stack([way_points_np,  path_np, img_np], axis=2)
        if show:
            imS = cv2.resize(img, (500, 500))  # Resize image.
            import matplotlib.pyplot as plt
            plt.imshow(imS)
            plt.show()
            cv2.imshow("output", imS)
            if cv2.waitKey() and 0xFF == ord("q"):
                cv2.destroyAllWindows()

        return img

    def solve_maze(self, start: tuple, end: tuple, radius:int=4,scale:int=1) -> list:
        start = ((-1,-1), start)
        end = ((-1,-1), end)
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
            kids = self.find_kids(out, visited_nodes_pos, explored_nodes_pos)
            self.append_kids(q, kids, end, explored_nodes_pos, radius=radius,scale=scale)

        fin_path = []
        self.find_fin_path(fin_path, out)
        fin_path.reverse()
        return fin_path

