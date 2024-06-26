import json

from PIL import Image as im
import numpy as np
from pathlib import Path


# 地图下载地址：https://steamcommunity.com/sharedfiles/filedetails/?id=230110279
#            https://readtldr.gg/simpleradar
# 目前只做了cache一张地图。通过一张网上cache的截图，将其缩小后二值化处理成为一张二维数组（网格化）。1 代表可通行，0代表障碍物。
# 二维数组的元素为list，list结构 [0/1 x坐标 y坐标]，二维数组元素的行列index，与坐标是一一对应关系。
# 另一种更为优雅的方式是采用navmesh方法把地图分块。
def print_bitmap(bit_map: np.array, target: tuple):
    sz = bit_map.shape
    (t_r, t_c) = target
    for i in range(sz[0]):
        for j in range(sz[1]):
            if i == t_r and j == t_c:
                print("2", end='')
            elif bit_map[i][j] == 0:
                print("1", end='')
            else:
                print(" ", end='')
        print("")


def preprocess(path, sz, thresh):
    """
    图像预处理,返回黑白视图
    :param path:
    :param sz:size
    :return:
    """
    img = im.open(path)
    imgSmall = img.resize(sz, resample=im.LANCZOS)
    filter = lambda x: 255 if x > thresh else 0
    imgSmall = imgSmall.convert('L').point(filter, mode='1')
    #imgSmall.show()
    return imgSmall


def image_to_nparray(img):
    """
    :param img: 单通道 0 1图像
    :return: 行*列*数据 数据格式[bool, x, y]
    """
    bit = np.array(img)
    bit_map = np.expand_dims(bit, axis=2)
    return bit_map


def generate_from_point(bit_map, point1, point2):
    # 计算可通行区域的坐标
    # point1 = [x1,y1, [行,列]]
    # return: 行*列*3[是否可行, x, y]
    x1, y1, id1 = point1[0], point1[1], point1[2]
    x2, y2, id2 = point2[0], point2[1], point2[2]
    dy = (y2 - y1) / (id2[0] - id1[0])
    dx = (x2 - x1) / (id2[1] - id1[1])
    # 根据标定点坐标对可行区生成坐标
    x = np.empty(bit_map.shape)
    y = np.empty(bit_map.shape)
    for i in range(bit_map.shape[0]):
        for j in range(bit_map.shape[1]):
            if bit_map[i][j][0]:  # 如果可通行，根据标定点1计算x y
                x[i][j][0] = dx * (j - id1[1]) + x1
                y[i][j][0] = dy * (i - id1[0]) + y1
    bit_map = np.append(bit_map, x, axis=2)
    bit_map = np.append(bit_map, y, axis=2)
    return bit_map, dx, dy


class Map:
    def __init__(self, name):
        self.name = name
        script_dir = Path(__file__).parent
        self.path = script_dir/".\dir\{}.png".format(self.name)

        with open(script_dir/".\dir\{}.json".format(self.name), "r") as f:
            conf = json.load(f)
            self.sz = (int(conf['scale_size'][0]), int(conf['scale_size'][1]))
            self.point1 = conf["point1"]  # 1点在地图中[x, y, 位图中行和列(对应Y和X)]
            self.point2 = conf["point2"]  # 2点在地图中[x, y, 位图中行和列(对应Y和X)]
            self.way_points = conf["way_points"]
            self.threshold = conf["threshold"]
            self.bomb_sites = [tuple(each) for each in conf["bomb_site"]]
        image = preprocess(self.path, self.sz, self.threshold)
        bit_map = image_to_nparray(image)
        # print_bitmap(bit_map, (187, 129)) # cl_showpos 1 来手动标定point1、2

        self.bit_map, self.dx, self.dy = generate_from_point(bit_map, self.point1, self.point2)


if __name__ == "__main__":
    # print("标定点 3", [(104-73)*dx+1739.25, (41-41)*dx+285.16 ,0 ])
    # 标定点 1 [-1081.97 1499.97 1772.09]       18*17   y*x
    # cache 标定点 2 ：[1739.25x 285.16y 1677.09] 41x73匪徒门上 y*x
    # 标定点 3 [3306.79 285.16 1677.09]   41*104
    # sz = (107, 78)  # (210, 140) 一行180个像素，不是180行
    # path = r"D:\PROJECT\BOT\map\dir\cache2.png"
    #
    cache = Map("de_dust2")




