### CSGO bot大战参考代码

#### 如何使用

1.调试好游戏环境

    游戏窗口化
    游戏切换为de_dust2地图的死亡竞赛经典模式
    控制台输入 mp_roundtime 60; mp_restartgame 1;(可选。如在服务器中游玩则不用，仅方便测试环节)

2.开启bot

    在pycharm中直接运行main.py
    或python main.py



#### 依赖
    建议py3.7版本
    pip install numpy
    pip install pymem
    pip install pywin32
    pip install opencv-python
    
#### 添加新地图流程
    
    0.找一张干净的CSGO地图，保存为de_dust2.png形式在map/dir/ 
        # 地图下载地址：https://steamcommunity.com/sharedfiles/filedetails/?id=230110279
        # https://readtldr.gg/simpleradar
    1.使用map_add_tool 中的 print_bitmap(bit_map, (187, 129)) 和游戏实际坐标
      来得出两个标定点poin1 poin2，写入你的de_dust2(可选名字).json下
    2.使用way_point_tool 在地图中点选你的路点，会被自动保存到json中
    3.如果为死斗模式，启用patrol；如果是爆破模式，启用act
    注：如使用该代码在公服，会导致VAC。不要试图用于邪恶用途。
       针对AI竞技，请进入服务器：
