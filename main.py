from api import api
from map import map_grid
from route import main as route
import time, cv2
import random



def find_nearst_pos(handle, bit_map, dx, dy, point1):
    """
    与point1的相对位置 对dx dy 取余数，得到当前index
    当前index为中心的8个点，取最近的非障碍点为最终位置
    :param handle: API
    :param dx:
    :param dy:
    :param point1: [x, y , [index_x,index_y]]
    :return: i_r, i_c
    """
    pos = handle.get_current_position()
    i_c = int((pos[0] - point1[0]) // dx + point1[2][1] + 1)
    i_r = int((pos[1] - point1[1]) // dy + point1[2][0] + 1)
    pos = route.find_kids(((-1, -1), (i_r, i_c)), [], bit_map,[])[1]
    if int(bit_map[(i_r, i_c, 0)]) == 0:
        print("NULL POSITION")
    return int(pos[1][0]), int(pos[1][1])


def get_nearest_way_point(way_points: list, cur: tuple):
    dis = [route.manhattan(cur, point) for point in way_points]
    print("dis",dis)
    print("way_points", way_points)
    return way_points[dis.index(min(dis))], dis.index(min(dis))


from route import main as path_find



import numpy as np


class Bot(object):
    def __init__(self, map: map_grid.Map, handle:api.CSAPI):
        self.path = []
        self.handle = handle
        self.bit_map, self.dx, self.dy, self.point1 = map.bit_map, map.dx, map.dy, map.point1
        self.way_points = [  (95, 124),  (82, 114), (77, 66), (33, 60), (47, 32), (91, 36),
                      (132, 39), (119, 86), (137, 105), (126, 117), (106, 114), (93, 127), (67, 142), (98, 175)]
        self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
        self.is_alive = not handle.is_alive()
        self.is_seeing_enemy = self.handle.is_seeing_enemy()
        self.bullets = self.handle.get_bullets(10)



    def update_bot(self):
        self.handle.set_walk([0,0,0,0,0,0])
        self.is_alive = not handle.is_alive()
        self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
        self.is_seeing_enemy = self.handle.is_seeing_enemy()
        self.bullets = self.handle.get_bullets(10)

    def draw_routes(self):
        # get map
        img_np = self.bit_map[:, :, 0]
        way_points_np = np.zeros(img_np.shape)
        path_np = np.zeros(img_np.shape)
        # draw waypoints
        for each in self.way_points:
            way_points_np[each] = 250

        # draw path
        for each in self.path:
            path_np[each] = 100
        # draw me
        way_points_np[self.cur_pos] = 200

        img = np.stack([way_points_np,  path_np, img_np], axis=2)
        imS = cv2.resize(img, (500, 500))  # Resize image.
        cv2.imshow("output", imS)
        if cv2.waitKey(25) and 0xFF == ord("q"):
            cv2.destroyAllWindows()


    def reroute(self):
        near, near_index = get_nearest_way_point(self.way_points, self.cur_pos)
        way_points = self.way_points[near_index:-1] + self.way_points[0:near_index]
        print("way_points", way_points)
        self.way_points = way_points

    def patrol(self):
        if self.is_seeing_enemy or self.is_alive is False:
            print(self.is_seeing_enemy, "is_seeing_enemy")
            print(self.is_alive, "self.is_alive")
            return
        for desti in self.way_points:
            self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
            start, end = ((-1, -1), self.cur_pos), ((-1, -1), desti)
            print("rounting ", self.cur_pos)
            self.path = path_find.solve_maze_a_star(start, end, self.bit_map)
            self.draw_routes()
            for each in self.path:
                x, y = self.bit_map[(each[0], each[1], 1)], self.bit_map[(each[0], each[1], 2)]
                print("walking to ", [x, y])
                if handle.set_walk_to([x, y, 0], [], [handle.is_seeing_enemy, handle.is_alive]) is False:
                    return


if __name__ == "__main__":
    handle = api.CSAPI(r"D:\PROJECT\BOT\api\csgo.json")
    cache = map_grid.Map("de_cache")
    time.sleep(0.1)
    bot = Bot(cache, handle)

    # 玩具代码，尽管把玩随便改。 很多实现由于鄙人水平原因有些笨拙，各位有兴趣可以自己用FSM写一个。
    # 地图抽象是依靠一张网图，如果出现bot 日墙，可能是地图精准不够。 你可以重新定位一下。在map类中找新坐标便可。
    while True:
        bot.draw_routes()
        try:
            bot.update_bot()
            if not bot.is_alive:
                bot.reroute()
            if bot.is_seeing_enemy:
                bot.handle.shoot()
                continue
            print("way points", bot.way_points)
            bot.draw_routes()
            bot.patrol()
        except:
            import traceback
            traceback.print_exc()
            pass