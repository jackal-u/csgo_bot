import queue, copy, operator
import numpy as np
import random
import cv2
from typing import List, Tuple
from scipy.spatial import distance
from scipy.spatial import KDTree as KDTrees
from sklearn.neighbors import KDTree
import rtree
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

from map import Map


class BiRRTSolver:
    def __init__(self, map_: Map):
        bit_map, dx, dy, point1 = map_.bit_map, map_.dx, map_.dy, map_.point1
        self.bitmap = bit_map
        self.point1 = point1
        bitmap_obstacles = np.squeeze(bit_map[:, :, 0])
        # convert obstacles in bitmap to KDtrees
        self.train = np.argwhere(bitmap_obstacles == False)
        # false 代表障碍物 true代表可通行
        self.obstacles = KDTree(self.train)
        self.gen_ava_coordinates()

    def gen_ava_coordinates(self):
        ## 根据point1，采用连通量提取算法生成可行区域
        avaliable_map = self.bitmap[:, :, 0]
        kernel = np.ones((3, 3))
        x = np.zeros(shape=avaliable_map.shape)
        x_, y_ = self.point1[2]
        x[x_, y_] = True
        last_sum = -1
        while np.sum(x) != last_sum:
            last_sum = np.sum(x)
            x = np.where(convolve2d(x, kernel, mode='same') > 0, True, False)
            x = np.logical_and(x, avaliable_map)
        plt.imshow(x)
        plt.title("real avaliable map")
        plt.show()
        self.ava_coordinates = np.argwhere(x == True).tolist()

    def check_collision(self, ele: tuple) -> bool:
        """ 检测这个点是否撞击 True表示撞上了"""
        ele = np.expand_dims(np.array(ele), axis=0)
        distances, indices = self.obstacles.query(ele, k=1)
        thres = 1
        if distances[0] < thres:
            return True  # yes, it collised
        return False  # no, its avaliable

    def head_random(self, step_num: int = 5, step_len: float = 3, prob: float = 0.99):
        """
        STree 随机探索 ETree 随机探索
        随机探索：
            八个方向上随机一个方向，然后走step_num步，每一步step_len长，
            如果某一步撞击则找寻其最近可用点返回
            然后加入到树
        返回：min(当前STree中探索节点到ETree的距离，当前ETree中探索节点到STree的距离), [(s_cur,e_nearst),(e_cur,s_nearst)]
        """
        if random.random() < prob:
            # 从可行list中随机采样一个可行节点
            target_point_s = self.ava_coordinates[np.random.randint(0, len(self.ava_coordinates))]
            target_point_e = self.ava_coordinates[np.random.randint(0, len(self.ava_coordinates))]
        else:
            # 最终点作为朝向点
            target_point_s = (self.end_node[0], self.end_node[1])
            target_point_e = (self.start_node[0], self.start_node[1])
        # 得到当前树中最近的一个节点
        nearest_node_s = self.STree.query_nearest_node(target_point_s[0], target_point_s[1])
        nearest_node_e = self.ETree.query_nearest_node(target_point_e[0], target_point_e[1])
        # 沿着可行节点的方向走stepsize,并检查路径上点是否遇到障碍
        ## 返回从nearest_node到target_point直线走step_num距离对应的网格坐标
        for i in range(step_num):
            vec = (target_point_s[0] - nearest_node_s[0], target_point_s[1] - nearest_node_s[1])
            # if norm is 0
            if vec[0] == 0 and vec[1] == 0:
                return [99999,99999],[99999,99999]
            # normalize
            vec = (vec[0] / np.sqrt(vec[0] ** 2 + vec[1] ** 2), vec[1] / np.sqrt(vec[0] ** 2 + vec[1] ** 2))
            x = int(nearest_node_s[0] + i * vec[0] * step_len)
            y = int(nearest_node_s[1] + i * vec[1] * step_len)
            if self.check_collision((x, y)):
                # todo:如果撞击则返回最近可用点
                x = int(nearest_node_s[0] + (i - 1) * vec[0] * step_len)
                y = int(nearest_node_s[1] + (i - 1) * vec[1] * step_len)
                break
        stepped_node_s = (x, y)
        for i in range(step_num):
            vec = (target_point_e[0] - nearest_node_e[0], target_point_e[1] - nearest_node_e[1])
            # if norm is 0
            if vec[0] == 0 and vec[1] == 0:
                return [99999,99999],[99999,99999]
            # normalize
            vec = (vec[0] / np.sqrt(vec[0] ** 2 + vec[1] ** 2), vec[1] / np.sqrt(vec[0] ** 2 + vec[1] ** 2))
            x = int(nearest_node_e[0] + i * vec[0] * step_len)
            y = int(nearest_node_e[1] + i * vec[1] * step_len)
            if self.check_collision((x, y)):
                # todo:如果撞击则返回最近可用点
                x = int(nearest_node_e[0] + (i - 1) * vec[0] * step_len)
                y = int(nearest_node_e[1] + (i - 1) * vec[1] * step_len)
                break
        stepped_node_e = (x, y)
        # 将这2个节点加入树中
        mid_node_s = TreeNode(x=stepped_node_s[0], y=stepped_node_s[1])
        self.STree.add_node(nearest_node_s, mid_node_s)
        mid_node_e = TreeNode(x=stepped_node_e[0], y=stepped_node_e[1])
        self.ETree.add_node(nearest_node_e, mid_node_e)
        # 计算最短距离
        nearest_node_s2e = self.ETree.query_nearest_node(mid_node_s[0], mid_node_s[1])
        dis_s2e = np.sqrt((nearest_node_s2e[0] - mid_node_s[0]) ** 2 + (nearest_node_s2e[1] - mid_node_s[1]) ** 2)
        if dis_s2e==0.0:
            print(1)
        nearest_node_e2s = self.STree.query_nearest_node(mid_node_e[0], mid_node_e[1])
        dis_e2s = np.sqrt((nearest_node_e2s[0] - mid_node_e[0]) ** 2 + (nearest_node_e2s[1] - mid_node_e[1]) ** 2)
        distances_l = [dis_e2s, dis_s2e] # E探索点到S最近点的距离， S探索点到E最近点的距离，
        nodes_l = [(nearest_node_e2s, mid_node_e), (mid_node_s, nearest_node_s2e)]
        return distances_l, nodes_l  # todo:111


    def draw_routes(self, solution: List[Tuple[int, int]], bit_map: np.array, show: bool = True) -> np.array:
        ## get map
        img_np = bit_map[:, :, 0]
        way_points_np = np.zeros(img_np.shape)
        path_np = np.zeros(img_np.shape)

        ## draw waypoints
        # for each in self.way_points:
        #     way_points_np[each] = 250

        ## draw path
        for each in solution:
            # clip ele to (0,200)
            each = (min(each[0], 199), min(each[1], 199))
            # assert each[0] < 199 and each[1] < 199
            assert each[0] < 200 and each[1] < 200
            path_np[each] = 100

        ## draw me
        # way_points_np[self.cur_pos] = 200
        img = np.stack([way_points_np, path_np, img_np], axis=2)
        if show:
            imS = cv2.resize(img, (500, 500))  # Resize image.
            import matplotlib.pyplot as plt
            plt.imshow(imS)
            plt.title(f"total {len(solution)} of points")
            plt.show()
            cv2.imshow("output", imS)
            cv2.waitKey(1)
        # if cv2.waitKey(10):
        #     cv2.destroyAllWindows()

        return img

    def solve_maze(self, start: tuple, end: tuple, radius: int = 1, iter: int = 5000, step_num: int = 10,
                   step_len: float = 1, prob:float=0.9,draw:int=0) -> list:
            # radius=3,iter=5000,step_num=10,step_len=1,prob=0.9,draw=True)
            # initialize treenode
            self.start_node = TreeNode(x=start[0], y=start[1])
            self.end_node = TreeNode(x=end[0], y=end[1])
            # intialize Tree
            self.STree = Tree(self.start_node)
            self.ETree = Tree(self.end_node)
            #  head random
            for i in range(iter):
                distances_l, nodes_list = self.head_random(step_num=step_num, step_len=step_len, prob=prob)
                nodes = nodes_list[distances_l.index(min(distances_l))]
                dis = min(distances_l)

                #  check if nodes in different tree were close enough
                if draw==2:
                    self.draw_routes(self.ETree.to_list()+self.STree.to_list(), self.bitmap)
                if dis < radius:
                    print("find a solution")
                    path_s2e = self.STree.get_path(nodes[0])
                    path_e2s = self.ETree.get_path(nodes[1])
                    path_e2s.reverse()
                    if ((path_s2e[-1][0] - path_e2s[0][0]) ** 2 + (path_s2e[-1][1] - path_e2s[0][1]) ** 2)>2:
                        print(path_s2e,path_e2s,dis,nodes)
                    path = [start]+path_s2e + path_e2s + [end]
                    print(path_s2e, path_e2s)
                    if draw==1:
                        self.draw_routes(path, self.bitmap)
                    return path
            print("no solution")
            return []


class TreeNode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.children = []

    # TypeError: 'TreeNode' object is not subscriptable
    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        else:
            raise ValueError("idx must be 0 or 1")

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def __repr__(self):
        return f"TreeNode({self.x}, {self.y})"


class Tree:
    def __init__(self, root):
        self.root = root
        self.node_list = [root]
        self.kdtree = KDTrees(np.array([(root.x, root.y)]))

    def add_node(self, parent, child):
        parent.add_child(child)
        self.node_list.append(child)
        self.kdtree = KDTrees(np.array([(node.x, node.y) for node in self.node_list]))

    def query_nearest_node(self, x, y):
        _, idx = self.kdtree.query(np.array([x, y]))
        return self.node_list[idx]

    def get_parent(self, node):
        return node.parent

    def get_path(self, node):
        path = []
        while node.parent:
            path.append((node.x, node.y))
            node = node.parent
        # reverse the path
        path.reverse()
        return path

    def to_list(self):
        # convert self.node_list to list of tuples
        return [(node.x, node.y) for node in self.node_list]
