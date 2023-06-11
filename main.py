import threading
from utils import gui
import keyboard
import win32gui

from api import api
from map import map_grid
from route import main as route
from utils import *
import time, cv2
import random
from route import AstarSolver, RRTSolver, BiRRTSolver
import numpy as np


class Bot(object):
    def __init__(self, map: map_grid.Map, handle:api.CSAPI):
        self.path = []
        #self.solver = BiRRTSolver(map_=map)
        self.solver = AstarSolver(map_=map)
        self.handle = handle
        self.map = map
        self.bit_map, self.dx, self.dy, self.point1 = map.bit_map, map.dx, map.dy, map.point1
        self.perception = self.bit_map[:, :, 0]*150
        way = [tuple(each) for each in map.way_points]
        way.reverse() if random.random() > 0.5 else 1
        self.way_points = way  # way.reverse() if random.random()>0.5 else way
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
        self.rounds = self.handle.get_rounds_played()
        self.bomb_location = self.handle.get_bomb_location()
        self.bomb_planted = self.handle.is_bomb_planted()
        self.team = self.handle.get_myteam()
        self.c4onme = self.handle.is_c4_on_me()

    def draw_routes(self):
        img_np = self.bit_map[:, :, 0]
        way_points_np = np.zeros(img_np.shape)
        path_np = np.zeros(img_np.shape)
        # draw waypoints
        for each in self.way_points:
            way_points_np[each] = 2
        # draw path
        for each in self.path:
            path_np[each] = 3
        # draw me
        way_points_np[self.cur_pos] = 4
        img = img_np + path_np + way_points_np
        img =np.clip(img, 0, 4)
        # 0-4 障礙物0 空閑區1 路点2 路徑3 自己4
        color = np.array([[138,138,138],[0,0,0],[10,255,108],[255,235,20],[245,67,22]])
        img = color[img.astype(int)]
        #imS = cv2.resize(img, (500, 500))  # Resize image.
        self.perception = img

    def reroute(self):
        print("reroute")
        near, near_index = get_nearest_way_point(self.way_points, self.cur_pos)
        way_points = self.way_points[near_index:-1] + self.way_points[0:near_index+1]
        self.way_points = way_points

    def patrol(self):
        if self.is_seeing_enemy or self.is_alive is False: #or self.bomb_planted
            print("patrol done")
            print(self.is_seeing_enemy, "is_seeing_enemy")
            print(self.is_alive, "self.is_alive")
            self.reroute()
            return
        for desti in self.way_points:
            self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
            start, end = self.cur_pos, desti
            print("rounting ", self.cur_pos, "to", desti)
            self.path = self.solver.solve_maze(start,end)
            self.draw_routes()
            for each in self.path:
                x, y = self.bit_map[(each[0], each[1], 1)], self.bit_map[(each[0], each[1], 2)]
                print("walking to ", [x, y])
                if handle.set_walk_to([x, y, 0], [], [handle.is_seeing_enemy, handle.is_alive, self.is_new_round]) is False:
                    return

    def is_new_round(self):
        if self.rounds == self.handle.get_rounds_played():
            return False
        print("new round")
        return True

    def plant(self):
        keyboard.press("e")
        time.sleep(5)
        keyboard.release("e")

    def defuse(self):
        print("defusing", self.bomb_location)
        self.handle.set_aim_to(self.bomb_location, mode = "defuse")
        window_handle = win32gui.FindWindow(None, u"Counter-Strike: Global Offensive - Direct3D 9")
        win32gui.SetForegroundWindow(window_handle)
        t0 = time.time()
        while time.time() - t0 < 10:
            keyboard.press("e")
        keyboard.release("e")

    def goto_plant(self):
        "随机选择炸点 然后安C4"
        bomb_site = random.choice(self.map.bomb_sites)
        if self.is_seeing_enemy or self.is_alive is False or self.bomb_planted:
            print("patrol done")
            print(self.is_seeing_enemy, "is_seeing_enemy")
            print(self.is_alive, "self.is_alive")
            self.reroute()
            return
        # picked_bombsite
        desti = bomb_site
        # walk
        self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
        start, end = self.cur_pos, desti
        print("rounting ", self.cur_pos, "to", desti)
        self.path = self.solver.solve_maze(start,end)
        if self.is_new_round():
            self.draw_routes()
            return
        self.draw_routes()
        for each in self.path:
            x, y = self.bit_map[(each[0], each[1], 1)], self.bit_map[(each[0], each[1], 2)]
            #print("walking to ", [x, y])
            if handle.set_walk_to([x, y, 0], [], [handle.is_seeing_enemy, handle.is_alive, self.is_new_round]) is False:
                #如果在子节点路上遇到敌人，直接终止整体行走
                return
            else:
                # 如果没遇到敌人，而是成功子节点
                # 比较成功节点是否是最终节点
                if each==desti:
                    self.plant()
                else:
                    continue

    def follow_c4(self):
        "for t only"
        c4_location = self.bomb_location
        desti = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1, custome=c4_location)
        # walk
        self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
        start, end = self.cur_pos, desti
        print("rounting ", self.cur_pos, "to", desti)
        self.path = self.solver.solve_maze(start,end)
        self.draw_routes()
        for each in self.path:
            x, y = self.bit_map[(each[0], each[1], 1)], self.bit_map[(each[0], each[1], 2)]
            print("walking to ", [x, y])
            if handle.set_walk_to([x, y, 0], [], [handle.is_seeing_enemy, handle.is_alive, handle.is_bomb_planted, self.is_new_round]) is False:
                # 如果在子节点路上遇到敌人，直接终止整体行走
                return
            else:
                # 如果没遇到敌人，而是成功子节点
                # 比较成功节点是否是最终节点
                continue

        pass

    def goto_c4(self):
        "for ct only, after planted"
        print("goto_c4!!!")
        c4_location = self.bomb_location
        if not c4_location:
            self.patrol()
            return
        desti = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1, custome=c4_location)
        # walk
        self.cur_pos = find_nearst_pos(handle, self.bit_map, self.dx, self.dy, self.point1)
        start, end = self.cur_pos, desti
        print("rounting ", self.cur_pos, "to", desti)
        self.path = self.solver.solve_maze(start,end)
        self.draw_routes()
        for each in self.path:
            x, y = self.bit_map[(each[0], each[1], 1)], self.bit_map[(each[0], each[1], 2)]
            print("walking to ", [x, y])
            if handle.set_walk_to([x, y, 0], [], [handle.is_seeing_enemy, handle.is_alive]) is False:
                # 如果在子节点路上遇到敌人，直接终止整体行走
                return
            else:
                # 如果没遇到敌人，而是成功子节点
                # 比较成功节点是否是最终节点
                if desti == each:
                    self.defuse()
                else:
                    continue

    def t(self):
        if not self.bomb_planted:
            if self.c4onme:
                self.goto_plant()
            else:
                self.follow_c4()
        else:
            bot.patrol()
            # bot.handle.shoot()

    def ct(self):
        if not self.bomb_planted:
            self.patrol()
        else:
            self.goto_c4()

    def act(self):
        if self.team == 2:
            self.t()
        else:
            self.ct()

    def run(self):
        self.should_stop = False
        while True:
            if self.should_stop or keyboard.is_pressed("q"):
                exit()
            bot.draw_routes()
            try:
                bot.update_bot()
                if not bot.is_alive:
                    print("im dead, reroute")
                    bot.reroute()
                    continue
                if bot.is_seeing_enemy:
                    bot.handle.shoot()
                    bot.reroute()
                    continue
                bot.draw_routes()
                bot.patrol()
                # bot.act()
            except:
                import traceback
                traceback.print_exc()
                pass
    def stop(self):
        self.should_stop = True


if __name__ == "__main__":
    handle = api.CSAPI(r"./api/csgo.json")
    print("waiting for game to start")
    de_dust2 = map_grid.Map("de_dust2")
    time.sleep(0.1)
    bot = Bot(de_dust2, handle)
    gui = GUI(bot)
    gui.mainloop()

    # 玩具代码，尽管把玩随便改。 很多实现由于鄙人水平原因有些笨拙，各位有兴趣可以自己用FSM写一个。
    # 地图抽象是依靠一张网图，如果出现bot 日墙，可能是地图精准不够。 你可以重新定位一下。在map类中找新坐标便可。
    """
    qtepn69725
    qfuq18360Z
    """

