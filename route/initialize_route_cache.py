import json

import numpy as np
import main as path_find
import threading
import map.map_grid as map_grip
import time
# import multiprocessing

map_names = ["de_dust2", "de_cache"]
route_cache = {}
thread_count = 4


class RouteCalThread(threading.Thread):
    def __init__(self, pos_arr: list, bitmap: np.array):
        threading.Thread.__init__(self)
        self.pos_arr = pos_arr
        self.bitmap = bitmap

    def run(self):
        global route_cache
        cache = route_cache
        for pos in self.pos_arr:
            reversed_pos = tuple(reversed(pos))
            if reversed_pos in cache:
                cache[str(pos)] = list(reversed(cache[reversed_pos]))
            else:
                cache[str(pos)] = path_find.solve_maze_a_star(((-1, -1), pos[0]), ((-1, -1), pos[1]), self.bitmap)


class MonitorThread(threading.Thread):
    def __init__(self, map_name, pos_arr_len):
        threading.Thread.__init__(self)
        self.map_name = map_name
        self.pos_arr_len = pos_arr_len

    def run(self):
        start_time = time.time()
        print(self.map_name, " start to initialize")
        global route_cache
        cache = route_cache
        while len(cache) < self.pos_arr_len:
            print(self.map_name, round(len(cache) / self.pos_arr_len * 100, 2), "%")
            time.sleep(1)
        print(self.map_name, "100%")
        print("time usage:", time.time() - start_time)


def init():
    global route_cache
    print("Start to initialize route cache")
    for map_name in map_names:
        map_obj = map_grip.Map(map_name)
        init_route_cache(map_name, map_obj.bit_map)
        with open(map_name + '_route_cache.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(route_cache))
        route_cache = {}


def init_route_cache(map_name, bitmap: np.array):
    pos_arr = []
    for start_x in range(len(bitmap)):
        for start_y in range(len(bitmap[0])):
            start_pos = (start_x, start_y)
            for end_x in range(len(bitmap)):
                for end_y in range(len(bitmap[0])):
                    end_pos = (end_x, end_y)
                    if start_pos == end_pos:
                        continue
                    else:
                        pos_arr.append((start_pos, end_pos))
    calculate(pos_arr, map_name, bitmap)


def calculate(pos_arr: list, map_name, bitmap: np.array):
    threads = []
    slice_len = int(len(pos_arr) / thread_count)
    for i in range(thread_count - 1):
        threads.append(RouteCalThread(pos_arr[i * slice_len:i * slice_len + slice_len], bitmap))
    threads.append(RouteCalThread(pos_arr[(thread_count - 1) * slice_len:], bitmap))
    for t in threads:
        t.start()
    monitor_thread = MonitorThread(map_name, len(pos_arr))
    monitor_thread.start()
    for t in threads:
        t.join()
    monitor_thread.join()
# TODO: 由于windows与python的原因，多线程性能不理想，考虑采用多进程或协程提高并行计算性能

# def cal(pos: tuple, bitmap: np.array):
#     return path_find.solve_maze_a_star(((-1, -1), pos[0]), ((-1, -1), pos[1]), bitmap)
#
#
# def calculate(pos_arr: list, map_name, bitmap: np.array):
#     global route_cache
#     with multiprocessing.Pool(processes=4) as p:
#         for pos in pos_arr:
#             reversed_pos = tuple(reversed(pos))
#             if reversed_pos in route_cache:
#             p.apply_async(cal, (route_cache, pos, bitmap))
#     monitor_thread = MonitorThread(map_name, len(pos_arr))
#     monitor_thread.start()
#     monitor_thread.join()


if __name__ == '__main__':
    init()
