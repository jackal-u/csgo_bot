from api import api
from map import map_grid
from route import main as route
import time


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
    i_c = int((pos[0]-point1[0])//dx + point1[2][1] + 1)
    i_r = int((pos[1]-point1[1])//dy + point1[2][0] + 1)
    pos = route.find_kids((None, (i_r, i_c)), [], bit_map)[1]
    if int(bit_map[(i_r, i_c, 0)]) == 0:
        print("NULL POSITION")
    print((pos[1][0], pos[1][1], 0))
    return int(pos[1][0]), int(pos[1][1])



from route import main as path_find
if __name__ == "__main__":
    handle = api.CSAPI(r"D:\PROJECT\BOT\api\csgo.json")
    cache = map_grid.Map("de_cache")
    bit_map = cache.bit_map
    dx = cache.dx
    dy = cache.dy
    point1 = cache.point1
    # while 1:
    time.sleep(0.1)
    ir0, ic0 = find_nearst_pos(handle, bit_map, dx, dy, point1)

    while True:
        time.sleep(0.5)
        print(find_nearst_pos(handle, bit_map, dx, dy, point1))
        for desti in [(98, 175), (81, 141), (95, 124) , (91, 131), (82, 114), (77, 66), (33, 60), (47, 32), (91, 36), (132, 39), (119, 86), (137, 105), (126, 117),  (106, 114), (93, 127)
        ,(67, 142), (98, 175)]:
            ir0, ic0 = find_nearst_pos(handle, bit_map, dx, dy, point1)
            start = (None, (ir0, ic0))
            end = (None, desti)

            t0 = time.time()
            path = path_find.solve_maze_a_star(start, end, bit_map)
            print("{}s, path finding done".format(time.time() - t0), path)

            for each in path:
                x = bit_map[(each[0], each[1], 1)]
                y = bit_map[(each[0], each[1], 2)]
                print("walking to ", [x, y])
                handle.set_walk_to([x, y, 0],  [handle.shoot])
                for i in range(5):
                    handle.shoot()


#