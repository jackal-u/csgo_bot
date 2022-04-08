

import win32api
import win32gui
import win32process
import winsound
import pymem
import ctypes
import time, json, math, random, numpy
from scipy.spatial import distance

"""
https://csgo.dumps.host/?class=CPlantedC4
用于测试的csgo账号（不要登录公网VAC服务器）:
账号:mmye252570
密码：ojpd6n9z

"""

def normalizeAngles(viewAngleX, viewAngleY):
    if viewAngleX > 89:
        viewAngleX -= 360
    if viewAngleX < -89:
        viewAngleX += 360
    if viewAngleY > 180:
        viewAngleY -= 360
    if viewAngleY < -180:
        viewAngleY += 360

    return viewAngleX, viewAngleY

class CSAPI:

    def __init__(self, path):
        with open(path) as conf:
            off_set_dict=json.load(conf)
        self.dwEntityList = int(off_set_dict["signatures"]["dwEntityList"])
        self.m_bGunGameImmunity = int(off_set_dict["netvars"]["m_bGunGameImmunity"])
        self.m_iHealth = int(off_set_dict["netvars"]["m_iHealth"])
        self.dwClientState_GetLocalPlayer = int(off_set_dict["signatures"]["dwClientState_GetLocalPlayer"])
        self.client_dll = 0
        self.handle = 0
        self.aim_y = 0
        self.aim_x = 0
        self.step = 0
        self.dwGameRulesProxy = int(off_set_dict["signatures"]["dwGameRulesProxy"])
        self.m_nBombSite  = int(off_set_dict["netvars"]["m_nBombSite"])
        self.m_bBombDefused = int(off_set_dict["netvars"]["m_bBombDefused"])
        self.m_bBombPlanted = int(off_set_dict["netvars"]["m_bBombPlanted"])
        self.m_bBombTicking = int(off_set_dict["netvars"]["m_bBombTicking"])
        self.m_flC4Blow = int(off_set_dict["netvars"]["m_flC4Blow"])
        self.is_c4_owner = int(off_set_dict["netvars"]["m_flC4Blow"])
        self.m_iCrosshairId = int(off_set_dict["netvars"]["m_iCrosshairId"])

        self.m_flTimerLength = int(off_set_dict["netvars"]["m_flTimerLength"])
        self.m_bSpottedByMask = int(off_set_dict["netvars"]["m_bSpottedByMask"])
        self.m_aimPunchAngle = int(off_set_dict["netvars"]["m_aimPunchAngle"])
        self.m_hActiveWeapon = int(off_set_dict["netvars"]["m_hActiveWeapon"])
        self.m_bSpotted = int(off_set_dict["netvars"]["m_bSpotted"])
        self.m_lifeState = int(off_set_dict["netvars"]["m_lifeState"])
        self.m_bDormant =int(off_set_dict["signatures"]["m_bDormant"])
        self.m_hMyWeapons = int(off_set_dict["netvars"]["m_hMyWeapons"])
        self.m_angEyeAnglesX = int(off_set_dict["netvars"]["m_angEyeAnglesX"])
        self.m_angEyeAnglesY = int(off_set_dict["netvars"]["m_angEyeAnglesY"])
        self.m_vecVelocity = int(off_set_dict["netvars"]["m_vecVelocity"])
        self.off_enginedll = 0
        self.m_dwBoneMatrix = int(off_set_dict["netvars"]["m_dwBoneMatrix"])
        self.m_iTeamNum = int(off_set_dict["netvars"]["m_iTeamNum"])
        self.dwClientState = int(off_set_dict["signatures"]["dwClientState"])
        self.dwClientState_ViewAngles = int(off_set_dict["signatures"]["dwClientState_ViewAngles"])
        self.m_vecOrigin = int(off_set_dict["netvars"]["m_vecOrigin"])
        self.m_vecViewOffset = int(off_set_dict["netvars"]["m_vecViewOffset"])
        self.m_iClip1= int(off_set_dict["netvars"]["m_iClip1"])
        self.dwLocalPlayer = int(off_set_dict["signatures"]["dwLocalPlayer"])
        self.dwForceAttack = int(off_set_dict["signatures"]["dwForceAttack"])
        self.dwForceAttack2 = int(off_set_dict["signatures"]["dwForceAttack2"])
        self.dwForceBackward = int(off_set_dict["signatures"]["dwForceBackward"])
        self.dwForceForward = int(off_set_dict["signatures"]["dwForceForward"])
        self.dwForceLeft = int(off_set_dict["signatures"]["dwForceLeft"])
        self.dwForceRight = int(off_set_dict["signatures"]["dwForceRight"])
        self.dwForceJump = int(off_set_dict["signatures"]["dwForceJump"])
        self.dwForceCrouch = int(off_set_dict["signatures"]["dwForceJump"]) + 0x24
        self.dwForceReload = int(off_set_dict["signatures"]["dwForceJump"]) + 0x30
        self.m_iItemDefinitionIndex=int(off_set_dict["netvars"]["m_iItemDefinitionIndex"])
        self.is_fire = 0
        self.bomb_location = []
        self.round = 0


        # todo:自动导入csgo.json为本类属性

        # Counter-Strike: Global Offensive 窗口标题 获得窗口句柄
        window_handle = win32gui.FindWindow(None, u"Counter-Strike: Global Offensive - Direct3D 9")
        if window_handle:
            print(window_handle)
            # 获得窗口句柄获得进程ID
            process_id = win32process.GetWindowThreadProcessId(window_handle)
            print(process_id)
            handle = pymem.Pymem()
            handle.open_process_from_id(process_id[1])
            self.handle = handle
            # 遍历当前进程调用的dll，获得client.dll的基地址
            list_of_modules = handle.list_modules()

            while list_of_modules is not None:
                tmp = next(list_of_modules)
                if tmp.name == "client.dll":
                    self.client_dll = tmp.lpBaseOfDll
                if tmp.name == "engine.dll":
                    self.off_enginedll = tmp.lpBaseOfDll
                if self.off_enginedll != 0 and self.client_dll != 0:
                    break
            # client = pymem.process.module_from_name(
            #     handle.process_handle,
            #     "client.dll"
            # ).lpBaseOfDll
            # engine = pymem.process.module_from_name(
            #     handle.process_handle,
            #     "engine.dll"
            # ).lpBaseOfDll
            # print("off_enginedll,client_dll", engine, client)
        else:
            print("didn't get the window handle")
            exit()
        # todo:已经得到了基地址，加上任意偏移就可读写表地址的数值

    def get_health(self):
            # 获取当前人物血量
            player=0
            # 如果p 为0 则为 当前 人的血量
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + player * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if entity != 0:
                health = self.handle.read_bytes(entity + self.m_iHealth, 4)
                health = int.from_bytes(health, byteorder='little')
                return [health]

    def is_new_round(self):
        if self.round == self.get_rounds_played():
            return False
        print("new round")
        self.round = self.get_rounds_played()
        return True

    def get_weapon(self, player_entity=0):
            # todo: 武器内容比较复杂，每个武器都是个单独的对象，每个人物都拥有一个武器64位的指针列表
            """
                The m_hMyWeapons array contains handles to all weapons equipped by the local player.
                We can apply skin and model values to those weapons' entities independent to which weapon the local player is holding in hands.
                self.client_dll+self.dwLocalPlayer 获得当前用户的引用LOCAL
                LOCAL+m_hMyWeapons 获得当前用户的武器数组array。
                for 遍历（10）当前用户武器数组，获得武器实体的引用V（每个元素添加偏移0x4）
                V指针通过 dwEntityList + (currentWeapon - 1) * 0x10 获得当前武器的元信息；
                currentWeapon + m_iItemDefinitionIndex获得当前武器的 具体型号。

                C4:49
                匪徒刀：59
                CT刀：42
                p2000:32
                glock：4
                :return 返回长度为8的一个list
            """
            if player_entity==0:
                #如果没输入指定玩家，默认获取当前玩家
                # if entity != 0:
                # 获取local基地址 self.client_dll + self.dwEntityList + 0*0x10
                local_add = self.handle.read_bytes(self.client_dll+self.dwLocalPlayer, 4)
                local_add = int.from_bytes(local_add, byteorder='little')
                # print(local_add)
                weapon_list = [0 for _ in range(8)]
                for i in range(8):
                    # 武器数组array遍历获得武器引用。
                    weapon_each = self.handle.read_bytes(local_add + self.m_hMyWeapons + i * 0x4, 4)
                    weapon_each = int.from_bytes(weapon_each, byteorder='little') & 0xfff               # 我也不知道为什么按位与 1111
                    #print("weapon_each:  " + str(weapon_each))
                    # 武器引用获得武器元信息。
                    weapon_meta = self.handle.read_bytes(self.client_dll + self.dwEntityList + (weapon_each - 1) * 0x10, 4)
                    weapon_meta = int.from_bytes(weapon_meta, byteorder='little')
                    #print("weapon_meta:  " + str(weapon_meta))
                    if weapon_meta == 0:
                        continue
                    # # 武器元信息获得武器index。
                    weapon_index = self.handle.read_uint(weapon_meta+self.m_iItemDefinitionIndex)
                    # print("weapon_index", weapon_index)
                    weapon_list[i] = weapon_index
                return weapon_list
            else:
                # print(local_add)
                weapon_list = [0 for _ in range(8)]
                for i in range(8):
                    # 武器数组array遍历获得武器引用。
                    weapon_each = self.handle.read_bytes(player_entity + self.m_hMyWeapons + i * 0x4, 4)
                    weapon_each = int.from_bytes(weapon_each, byteorder='little') & 0xfff  # 我也不知道为什么按位与 1111
                    #print("weapon_each:  " + str(weapon_each))
                    # 武器引用获得武器元信息。
                    weapon_meta = self.handle.read_bytes(self.client_dll + self.dwEntityList + (weapon_each - 1) * 0x10,
                                                         4)
                    weapon_meta = int.from_bytes(weapon_meta, byteorder='little')
                    #print("weapon_meta:  " + str(weapon_meta))
                    if weapon_meta == 0:
                        continue
                    # # 武器元信息获得武器index。
                    weapon_index = self.handle.read_uint(weapon_meta + self.m_iItemDefinitionIndex)
                    # print("weapon_index", weapon_index)
                    weapon_list[i] = weapon_index
                return weapon_list

    def get_current_xy(self):
        """
        用于获得当前人物指针的指向，x轴(+180-180)，y轴(+-90)
        :return 返回长度为2的一个list
        """
        # player = 0
        # entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + player * 0x10, 4)  # 10为每个实体的偏移
        # entity = int.from_bytes(entity, byteorder='little')
        # local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer) # local_player 和entity_list[0]都为玩家
        # 玩家实体的地址，都为无符号整数uint而不是int。
        client_state = self.handle.read_uint(self.off_enginedll+self.dwClientState)
        view_x = self.handle.read_float((client_state + self.dwClientState_ViewAngles))
        view_y = self.handle.read_float((client_state + self.dwClientState_ViewAngles + 0x4))

        print("client_state", client_state)
        print("view_x, view_y", view_x, view_y)
        list = []
        # if entity != 0:
        #     x = self.handle.read_uint((entity + self.m_angEyeAnglesX))
        #     x&=0x8000
        #
        #     y = self.handle.read_uint(entity + self.m_angEyeAnglesY)
        #     y&=0x8000
        view_x, view_y = normalizeAngles(view_x, view_y)

        list.append(view_x)
        list.append(view_y)
        return list
    
    def get_current_position(self):
        """
        获得当前玩家的所在位置，两个维度
        :return:
        """

        list =[]
        aimlocalplayer = self.handle.read_uint(self.client_dll+self.dwLocalPlayer)
        vecorigin = self.handle.read_uint(aimlocalplayer + self.m_vecOrigin)

        localpos1 = self.handle.read_float(( aimlocalplayer + self.m_vecOrigin))  #+ self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x104)
        localpos2 = self.handle.read_float(( aimlocalplayer + self.m_vecOrigin+0x4))   #+ self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x108)
        localpos3 = self.handle.read_float((aimlocalplayer + self.m_vecOrigin + 0x8))  #+ self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x10C)
        list.append(localpos1)
        list.append(localpos2)
        list.append(localpos3)
        return list

    def get_enemy_position(self):
        """
        输出 长度为15的数组，每三个代表一个敌人的位置，他们按照内存顺序排序

        :return:
        """
        # list=[0 for i in range(15)]
        list = []
        counter = 0
        aimlocalplayer = self.handle.read_uint(self.client_dll+self.dwLocalPlayer)
        # 得到敌人的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        enemy_num = 0
        for i in range(64):

            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + i * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if (entity != 0):  # 实体非空，则进行处理
                team = self.handle.read_uint(entity + self.m_iTeamNum)
                # 实体 + 队伍偏移 == local_player + 队伍偏移 来判断是否是友军
                if (my_team == team):
                    # 友军
                    # 敌军
                    pass
                    # aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                    # enemypos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                    # enemypos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                    # enemypos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                    #
                    # list.append(enemypos1)
                    # list.append(enemypos2)
                    # list.append(enemypos3)
                    # enemy_num += 3
                else:
                    if counter < 5:
                        # # 敌军
                        aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                        enemypos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                        enemypos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                        enemypos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                        list.append(enemypos1)
                        list.append(enemypos2)
                        list.append(enemypos3)
                        counter += 1
        return  list

    def get_enemy_position_single(self):
        """
        输出 长度为15的数组，每三个代表一个敌人的位置，他们按照内存顺序排序

        :return:
        """
        # list=[0 for i in range(15)]
        list = []
        counter = 0
        aimlocalplayer = self.handle.read_uint(self.client_dll+self.dwLocalPlayer)
        # 得到敌人的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        enemy_num = 0
        for i in range(64):

            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + i * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if (entity != 0):  # 实体非空，则进行处理
                team = self.handle.read_uint(entity + self.m_iTeamNum)
                # 实体 + 队伍偏移 == local_player + 队伍偏移 来判断是否是友军
                if (my_team == team):
                    # 友军
                    # 敌军
                    pass
                    # aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                    # enemypos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                    # enemypos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                    # enemypos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                    #
                    # list.append(enemypos1)
                    # list.append(enemypos2)
                    # list.append(enemypos3)
                    # enemy_num += 3
                else:
                    if counter < 1:
                        # # 敌军
                        aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                        enemypos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                        enemypos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                        enemypos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                        list.append(enemypos1)
                        list.append(enemypos2)
                        list.append(enemypos3)
                        counter += 1
        return  list

    def get_friendly_position(self):
        """
        输出 长度为15的数组，每三个代表一个敌人的位置，他们按照内存顺序排序
        友军位置，包括自己的位置
        :return:
        """
        # list=[0 for i in range(15)]
        list = []

        aimlocalplayer = self.handle.read_uint(self.client_dll+self.dwLocalPlayer)
        # 得到人类的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        for i in range(64):
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + i * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if (entity != 0):  # 实体非空，则进行处理
                team = self.handle.read_uint(entity + self.m_iTeamNum)
                # 实体 + 队伍偏移 == local_player + 队伍偏移 来判断是否是友军
                if (my_team == team):
                    # 友军
                    aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                    pos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                    pos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                    pos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                    list.append(pos1)
                    list.append(pos2)
                    list.append(pos3)
                else:
                    # # 敌军
                   pass
        return  list

    def get_enemy_health(self):
        """
                输出 长度为5的数组,内存顺序排序
                :return:
                """
        # list=[0 for i in range(15)]
        list = []
        counter = 0
        aimlocalplayer = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        # 得到敌人的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        for i in range(64):
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + i * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if (entity != 0):  # 实体非空，则进行处理
                team = self.handle.read_uint(entity + self.m_iTeamNum)
                # 实体 + 队伍偏移 == local_player + 队伍偏移 来判断是否是友军
                if (my_team == team):
                    # 友军
                    pass

                else:
                    if counter < 5:
                        # todo: 敌人血量，开局应重置为100
                        # # 敌军
                        # 获取当前人物血量
                        health = self.handle.read_bytes(entity + self.m_iHealth, 4)
                        health = int.from_bytes(health, byteorder='little')
                        list.append(health)
                        counter+=1
        return list

    def set_attack2(self):
        # 测试中，无作用
        self.handle.write_int(self.client_dll + self.dwForceAttack2, -1)

    def set_attack(self, i):
        # 测试中，无作用
        self.is_fire = int(i)
        if int(i) == 6:
            self.handle.write_int(self.client_dll + self.dwForceAttack, int(i))

    def set_aim_to(self, to_pos_list, mode=None, smooth=1):
        # [to_x, to_y, to_z]
        local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        punchx = self.handle.read_float(local_player + self.m_aimPunchAngle)
        punchy = self.handle.read_float(local_player + self.m_aimPunchAngle + 0x4)
        pos = self.get_current_position()
        posx = pos[0]
        posy = pos[1]
        posz = pos[2]
        e_pos = to_pos_list
        e_posx = e_pos[0]
        e_posy = e_pos[1]
        e_posz = e_pos[2] -6 #- random.randint(0, 20)
        targetline1 = e_posx - posx
        targetline2 = e_posy - posy
        targetline3 = e_posz - posz
        dis = distance.euclidean(to_pos_list[0:2], self.get_current_position()[0:2])

        if targetline2 == 0 and targetline1 == 0:
            yaw = 0
            if targetline3 > 0:
                pitch = 269
            else:
                pitch = 89
        else:
            yaw = (math.atan2(targetline2, targetline1) * 180 / math.pi)
            if yaw < 0:
                yaw += 360
            hypotenuse = math.sqrt(
                (targetline1 * targetline1) + (targetline2 * targetline2) + (targetline3 * targetline3))
            pitch = (math.atan2(-targetline3, hypotenuse) * 180 / math.pi)
            if pitch < 0:
                pitch += 360
        pitch, yaw = normalizeAngles(pitch, yaw)
        enginepointer = self.handle.read_uint(self.off_enginedll + self.dwClientState)
        try:
            if mode == "walk":
                for i in range(10):
                    cur_pitch = self.handle.read_float((enginepointer + self.dwClientState_ViewAngles))
                    cur_yaw = self.handle.read_float((enginepointer + self.dwClientState_ViewAngles + 0x4))
                    d_pitch, d_yaw = normalizeAngles((pitch - cur_pitch), (yaw - cur_yaw))
                    pitch = cur_pitch + d_pitch / 10
                    yaw = cur_yaw + d_yaw / 10
                    self.handle.write_float((enginepointer + self.dwClientState_ViewAngles), 0.5)
                    self.handle.write_float((enginepointer + self.dwClientState_ViewAngles + 0x4), yaw)

            else:
                cur_pitch = self.handle.read_float((enginepointer + self.dwClientState_ViewAngles))
                cur_yaw = self.handle.read_float((enginepointer + self.dwClientState_ViewAngles+ 0x4))

                d_pitch, d_yaw = normalizeAngles((pitch - cur_pitch), (yaw - cur_yaw))

                pitch = cur_pitch + d_pitch/(smooth)
                yaw = cur_yaw + d_yaw/(smooth)

                pitch = pitch - punchx
                yaw = yaw - punchy
                # pitch, yaw = normalizeAngles(pitch, yaw)
                self.handle.write_float((enginepointer + self.dwClientState_ViewAngles), pitch)
                self.handle.write_float((enginepointer + self.dwClientState_ViewAngles + 0x4), yaw )
        except TypeError:
            pass


    # import math
    # def instant_stop(self):
    #     local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
    #     v0 = self.handle.read_float((local_player + self.m_vecVelocity))
    #     v1 = self.handle.read_float((local_player + self.m_vecVelocity + 0x4))
    #     v2 = self.handle.read_float((local_player + self.m_vecVelocity + 0x8))
    #     print("vo, v1, v2",v0,v1,v2)
    #     print("vo v1 total ", math.sqrt(v0*v0+v1*v1))

    def seeing_enemy(self):
        """
        :return:看到的敌人 位置数组 三个一组
        """
        # list=[0 for i in range(15)]
        list = []
        aimlocalplayer = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        # 得到敌人的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        for i in range(64):
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + i * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if entity != 0:  # 实体非自己，则进行处理
                team = self.handle.read_uint(entity + self.m_iTeamNum)
                # 实体 + 队伍偏移 == local_player + 队伍偏移 来判断是否是友军
                if my_team != team:
                    # 敌军
                    # 如被发现，拿出这个活着的敌人的引用，然后加入list
                    spot = str(bin(self.handle.read_uint(entity + self.m_bSpottedByMask)))
                    # spottedbymask(二进制) 是指当前实体那些人看到; 返回值 0b0000001 从右往左数 第一个为玩家；
                    if bool(int(spot[-1])) or self.get_spy_entity() == entity:   # https://guidedhacking.com/threads/csgo-how-to-use-m_bspottedbymask-visibility-check.13950/
                        # 如果敌人被我看到 or 如果这个人看到了我=====>进入死亡名单
                        if not self.handle.read_uint(entity + self.m_lifeState):
                            aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                            enemypos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                            enemypos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                            enemypos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                            list.append(enemypos1)
                            list.append(enemypos2)
                            list.append(enemypos3)


        return list


    def test_ob(self):
        """
                :return:看到的敌人 位置数组 三个一组
                """
        # list=[0 for i in range(15)]
        list = []
        aimlocalplayer = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        # 得到敌人的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        for i in range(64):
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + i * 0x10, 4)  # 10为每个实体的偏移
            entity = int.from_bytes(entity, byteorder='little')
            if entity != 0:  # 实体非自己，则进行处理
                team = self.handle.read_uint(entity + self.m_iTeamNum)
                # 实体 + 队伍偏移 == local_player + 队伍偏移 来判断是否是友军
                if my_team != team:
                    # 敌军
                    # 如被发现，拿出这个敌人的引用，然后加入list
                    spot = str(bin(self.handle.read_uint(entity + self.m_bSpottedByMask)))
                    # print("m_bSpottedByMask", spot, bool(int(spot[-1])), entity)
                    if bool(int(spot[-1])):   # spotted 是是否被队友看到； spottedbymask(二进制) 是被那些人看到
                        print("m_bSpottedByMask", spot, bool(int(spot[-1])), entity)
                        aimplayerbones = self.handle.read_uint(entity + self.m_dwBoneMatrix)
                        enemypos1 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x0C)
                        enemypos2 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x1C)
                        enemypos3 = self.handle.read_float(aimplayerbones + 0x30 * 1 + 0x2C)
                        list.append(enemypos1)
                        list.append(enemypos2)
                        list.append(enemypos3)
        print(list)


    def instant_stop(self):
        v = self.get_velocity()
        while v > 3:
            self.set_walk([0,0,0,0,0,0])

    def is_alive(self):
        """
        0 alive; 1 dead; 2 spawning
        :return:
        """
        local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        alive = self.handle.read_uint(local_player + self.m_lifeState)
        return alive


    def is_seeing_enemy(self):
        if len(self.seeing_enemy()) == 0:
            return False
        else:
            return True

    def set_walk_to(self, to_pos_list, do_list, ends):
        # to_pos_list = [to_x, to_y, to_z], evens_func = [bool_fun, bool_func], end_do = do_func
        # walk to target position by W+jump
        # if vlocity<3 , jump
        for end in ends:
            if end():
                for do in do_list:
                    do()
                print("stop walk for enemy spotted/dead")
                return False
        d = distance.euclidean(to_pos_list[0:2], self.get_current_position()[0:2])
        t0 = time.time()
        while d > 40:
            if time.time()-t0 > 4:
                raise TimeoutError
            for end in ends:
                if end():
                    for do in do_list:
                        do()
                    print("stop walk for triggered event")
                    return False
            self.set_aim_to(to_pos_list, mode="walk")#
            self.set_walk([1, 0, 0, 0, 0, 0])
            d = distance.euclidean(to_pos_list[0:2], self.get_current_position()[0:2])
            v = self.get_velocity()
            if v < 2:
                self.set_walk([1, 0, 0, 0, 1, 0])
        self.set_walk([0, 1, 0, 0, 0, 0])
        self.set_walk([0, 0, 0, 0, 0, 0])
        print("walk done", to_pos_list, d)
        return True


    def set_aim(self, list):
        # [pitch, yaw]
        # +-90  +-180
        pitch = self.aim_y + list[0]*0.15  # 0.25
        yaw = self.aim_x + list[1]*0.15 #
        print("pitch  yaw",pitch,yaw)
        # self.aim_y = list[0]
        # self.aim_x = list[1]
        self.aim_y = pitch
        self.aim_x = yaw
        # 下面是重置代码，用于reset极端情况，避免不必要的训练
        if pitch >= +80.0:
            print("protected!")
            self.aim_y = 80.0
        if pitch <= -80.0:
            self.aim_y = -80.0

        if yaw >= +180:
            print("protected!")
            self.aim_x = 180.0
        if yaw <= -180:
            print("protected!")
            self.aim_x = -180.0
        print("俯仰角   ",self.aim_y ,'方位角：  ' , self.aim_x)
        enginepointer = self.handle.read_uint(self.off_enginedll + self.dwClientState)
        self.handle.write_float((enginepointer + self.dwClientState_ViewAngles), self.aim_y)
        self.handle.write_float((enginepointer + self.dwClientState_ViewAngles + 0x4), self.aim_x)

        pos = self.get_current_position()
        posx = pos[0]
        posy = pos[1]
        posz = pos[2]
        e_pos = self.get_enemy_position()
        e_posx = e_pos[0]
        e_posy = e_pos[1]
        e_posz = e_pos[2]
        targetline1 = e_posx - posx
        targetline2 = e_posy - posy
        targetline3 = e_posz - posz

        if targetline2 == 0 and targetline1 == 0:
            yaw = 0
            if targetline3 > 0:
                pitch = 269
            else:
                pitch = 89
        else:
            yaw = (math.atan2(targetline2, targetline1) * 180 / math.pi)
            if yaw < 0:
                yaw += 360
            hypotenuse = math.sqrt(
                (targetline1 * targetline1) + (targetline2 * targetline2) + (targetline3 * targetline3))
            pitch = (math.atan2(-targetline3, hypotenuse) * 180 / math.pi)
            if pitch < 0:
                pitch += 360

        pitch, yaw = normalizeAngles(pitch, yaw)
        #如果训练经过200步，角度差距还大于10，则进行重置；重置到敌人脑袋附近
        if self.steps%60 == 0: # and ( abs(cur_zuoyou - yaw) > 10  or abs(cur_shang_xia - pitch) > 20) and random.random()<0.3
            print("RESET!!!!")
            self.aim_x = yaw + random.random() * 2
            self.aim_y = pitch + random.random() * 2
            print("【重置！！】俯仰角   ", self.aim_y, '方位角：  ', self.aim_x)

            #winsound.Beep(2000, 200)
            self.steps += 1
            return
        self.steps += 1
        print("steps: ", self.steps)


    def set_reset_aim(self,is_reset,list):
        if is_reset:
            pass
            # self.aim_x = list [0]
            # self.aim_y = list [1]
            # enginepointer = self.handle.read_uint(self.off_enginedll + self.dwClientState)
            # self.handle.write_float((enginepointer + self.dwClientState_ViewAngles), self.aim_y)
            # self.handle.write_float((enginepointer + self.dwClientState_ViewAngles + 0x4), self.aim_x)

    def set_walk(self,list):
        # [wasd jump attack] as 0or1
        # 下蹲还没有做，正在探讨方法
        if len(list)!=6:
            print("WASD长度不为6")
        self.handle.write_int(self.client_dll + self.dwForceForward, list[0])
        self.handle.write_int(self.client_dll + self.dwForceBackward, list[1])
        self.handle.write_int(self.client_dll + self.dwForceLeft, list[2])
        self.handle.write_int(self.client_dll + self.dwForceRight, list[3])
        self.handle.write_int(self.client_dll + self.dwForceJump, list[4])
        if list[5]:
            self.handle.write_int(self.client_dll + self.dwForceAttack, 6)

    def get_velocity(self):
        # 0-250
        # enginepointer = self.handle.read_uint(self.off_enginedll + self.dwClientState)
        local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)  # local_player 和entity_list[0]都为玩家
        return abs(self.handle.read_float((local_player + self.m_vecVelocity + 0x4)))

    def get_bullets(self, i: int):
        """
        i = 0 knife, 1 pistol, 2 rifle, 10 current
        :param i:
        :return:
        """
        try:
            local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
            if i == 10:
                active_weapon = self.handle.read_uint(local_player + self.m_hActiveWeapon) & 0xfff
                weapon_meta = self.handle.read_bytes(self.client_dll + self.dwEntityList + (active_weapon - 1) * 0x10, 4)
                weapon_meta = int.from_bytes(weapon_meta, byteorder='little')
                bullets_num = self.handle.read_uint(weapon_meta + self.m_iClip1)

                return bullets_num
            else:

                # 武器数组array遍历获得武器引用。
                weapon_list = [self.handle.read_bytes(local_player + self.m_hMyWeapons + i * 0x4, 4) for i in range(8)]
                weapon_list = [int.from_bytes(each, byteorder='little') & 0xfff for each in weapon_list]
                weapon_meta = self.handle.read_bytes(self.client_dll + self.dwEntityList + (weapon_list[i] - 1) * 0x10, 4)
                weapon_meta = int.from_bytes(weapon_meta, byteorder='little')
                bullets_num = self.handle.read_uint(weapon_meta + self.m_iClip1)
                return bullets_num
        except:
            import traceback
            traceback.print_exc()
            return 30

    def get_reward(self):
        """
        奖励计算规则：
        +敌人血量与上一时间帧数之间血量的差值*800。
        #+100/当前瞄准和目标位置的XY轴距离。
        #-当前瞄准和目标位置的XY轴距离
        -固定偏移
        空枪惩罚

        :return:
        """
        total_blood = 0
        health_list = self.get_enemy_health()
        for each in health_list:
            total_blood += each
        # 这里计算血量减少的值作为奖赏
        blood_reward  = abs(self.enemy_heath - total_blood) * 8000
        reward = blood_reward
        self.enemy_heath = total_blood

        print('blood_reward: ', reward)
        # XXXXXXXXXXXXXXXXXXX
        # todo:如果瞄准准星很靠近预期方向那就基于更多的reward，且reward最好取连续值
        pos = self.get_current_position()
        posx = pos[0]
        posy = pos[1]
        posz = pos[2]
        e_pos = self.get_enemy_position()
        e_posx = e_pos[0]
        e_posy = e_pos[1]
        e_posz = e_pos[2]
        targetline1 = e_posx - posx
        targetline2 = e_posy - posy
        targetline3 = e_posz - posz

        if targetline2 == 0 and targetline1 == 0:
            yaw = 0
            if targetline3 > 0:
                pitch = 270
            else:
                pitch = 90
        else:
            yaw = (math.atan2(targetline2, targetline1) * 180 / math.pi)
            if yaw < 0:
                yaw += 360
            hypotenuse = math.sqrt(
                (targetline1 * targetline1) + (targetline2 * targetline2) + (targetline3 * targetline3))
            pitch = (math.atan2(-targetline3, hypotenuse) * 180 / math.pi)
            if pitch < 0:
                pitch += 360

        pitch, yaw = normalizeAngles(pitch, yaw)
        cur = self.get_current_xy()
        cur_shang_xia = cur[0]
        cur_zuoyou = cur[1]
        # print("x_grad",pitch,"y_grad",yaw)
        print("当前俯仰角：", cur_shang_xia, "当前方位角", cur_zuoyou)
        print("正确俯仰角", pitch, "正确方位角", yaw)
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

        # # 如果 位置没有达到期望值 就基于惩罚
        # if abs(cur_zuoyou - yaw) > 30 :
        #     reward -= (abs(cur_zuoyou - yaw)-30)*(abs(cur_zuoyou - yaw)-30)
        # if abs(cur_shang_xia - pitch) > 80 :
        #     # reward -= (abs(cur_shang_xia - pitch)-15)*(abs(cur_shang_xia - pitch)-15)*5
        #     reward = 0
        #
        #reward += 100/(abs(min((cur_zuoyou - yaw), (360-(cur_zuoyou - yaw))))+ abs(cur_shang_xia - pitch)*1.5)  #  这个可求导的奖励函数是一切的关键！  这个水平角的计算有问题，不应该是取顺时针角，而应该是取最小夹角。
        #reward -= (abs(cur_shang_xia - pitch))*(abs(cur_shang_xia - pitch))*0.05 # reward上下偏移惩罚
        #reward -= abs(min((cur_zuoyou - yaw), (360-(cur_zuoyou - yaw))))*0.05 # 左右偏移惩罚
        reward -= 1   # 手动偏移
        # # 下面添加 基于行为的奖励，而不是基于状态的奖励。
        # if cur_shang_xia > pitch:
        #     # 当前瞄准位置比较大，对减小的行为给予奖励，增大的行为给予惩罚
        #     if cur_shang_xia > self.last_shangxia:
        #         reward -= 20
        #     elif cur_shang_xia < self.last_shangxia:
        #         reward += 20
        #     else:
        #         reward -= 10
        #
        # else:
        #     # 当前瞄准位置比较小，对加大的行为给予奖励，减小的行为给予惩罚
        #     if cur_shang_xia > self.last_shangxia:
        #         reward += 20
        #     elif cur_shang_xia < self.last_shangxia:
        #         reward -= 20
        #     else:
        #         reward -= 10
        #
        #
        # if cur_zuoyou > yaw:
        #     # 当前瞄准位置比较大，对减小的行为给予奖励，增大的行为给予惩罚
        #     if cur_zuoyou > self.last_zuoyou:
        #         reward -= 20
        #     elif cur_zuoyou < self.last_zuoyou:
        #         reward += 20
        #     else:
        #         reward -= 10
        # else:
        #     # 当前瞄准位置比较小，对加大的行为给予奖励，减小的行为给予惩罚
        #     if cur_zuoyou > self.last_zuoyou:
        #         reward += 20
        #     elif cur_zuoyou < self.last_zuoyou:
        #         reward -= 20
        #     else:
        #         reward -= 10

        # self.last_shangxia = cur_shang_xia
        # self.last_zuoyou = cur_zuoyou

        # 空枪惩罚
        if self.is_fire == 1 and blood_reward == 0:
            reward -= 100
            self.is_fire = 0

        print("STEPS:", self.steps)
        print("FINAL REWARD", reward)
        self.steps += 1

        return reward


    def get_all_situation(self):
        """
        [hp, view_y(pitch),view_x(yaw),  pos1,pos2,pos3  ,  my_weapon x 8 ,  enemy_position X 15 , enemy_health x 5]

        :return:
        """
        list = self.get_health() + self.get_current_xy() + self.get_current_position() + self.get_weapon() + self.get_enemy_position() + self.get_enemy_health()
        return list


    def get_aim_situation(self):
        """
        由于目前我们技术比较菜，之前的那个all_situation明显过于复杂，我们现在假设一个简单的情景：
        我们拿着AK，站立不动，操作维度仅仅为：是否开火，瞄准位置
                [1,     +-90 , +- 180]      3
                            反馈维度：瞄准位置，自己位置，单个敌人位置，敌人健康
                [view_y(pitch),view_x(yaw),  pos1,pos2,pos3  , enemy_position X 3 , reward x 1。 ] 9 维度

                :return:
                """
        list =  self.get_current_xy() + self.get_current_position() + self.get_enemy_position_single() + [self.get_reward()]
        return list


    def get_spy_index(self):
        """
        读取 本地玩家的spottedbymask属性
        spottedbymask解释：
            如果当前玩家没被人发现，返回 ['0',  'b', '0']
            如果在4个敌人的对局中，被第3个敌人发现，返回 ['0','0', '1', '0', 'b', '0']
        这个函数，返回第一个 发现玩家的敌人index。 上例子中，为 “2”

        那么spotted属性是什么? 是指当前对象是否被被自己和同伴发现
        :return:
        """
        local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)  # local_player 和entity_list[0]都为玩家
        spot_list = list(bin(self.handle.read_uint(local_player + self.m_bSpottedByMask)))
        spot_list.reverse()
        for index, each_ob in enumerate(spot_list):
            if len(spot_list) == 3:  # 不被人发现，返回NONE
                return None
            if each_ob == '1':  # 被人发现，返回index
                return index


    def get_spy_entity(self):
        """
        返回第一个看到玩家的敌人的引用(内存地址);
        可参照get_spy_index方法
        :return:
        """
        index = self.get_spy_index()
        if index is not None:
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + index * 0x10, 4)
            entity = int.from_bytes(entity, byteorder='little')
            return entity
        return None

    def get_myteam(self):
        "2=terrorist 3=ct"
        aimlocalplayer = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        # 得到敌人的偏移
        my_team = self.handle.read_uint(aimlocalplayer + self.m_iTeamNum)
        return my_team
    def is_c4_on_me(self):
        localplayer = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        weapons = self.get_weapon(localplayer)
        if 49 in weapons:
           return 1
        else:
            return 0

    def get_bomb_location(self):
        """
        更新炸弹位置，如被下包，返回最后的位置
        :return:
        """
        # 搜索玩家 检查是否有C4 如果有 返回位置
        for index in range(0, 64):
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + index * 0x10, 4)
            entity = int.from_bytes(entity, byteorder='little')
            if 49 in self.get_weapon(entity) and entity!=0:
                localpos1 = self.handle.read_float((entity + self.m_vecOrigin))  # + self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x104)
                localpos2 = self.handle.read_float((entity + self.m_vecOrigin + 0x4))  # + self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x108)
                localpos3 = self.handle.read_float((entity + self.m_vecOrigin + 0x8))  # + self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x10C)
                self.bomb_location = [localpos1, localpos2, localpos3]
                print("bomb_location [dropped]", self.bomb_location)
                return [localpos1, localpos2, localpos3]

        # 搜索ID=49的对象 如果有 返回位置
        for index in range(64, 600):
            entity = self.handle.read_bytes(self.client_dll + self.dwEntityList + index * 0x10, 4)
            entity = int.from_bytes(entity, byteorder='little')
            if entity!=0:
                try:
                    entity_index = self.handle.read_uint(entity + self.m_iItemDefinitionIndex)
                except:
                    continue
                if entity_index == 49:
                    localpos1 = self.handle.read_float((entity + self.m_vecOrigin))  # + self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x104)
                    localpos2 = self.handle.read_float((entity + self.m_vecOrigin + 0x4))  # + self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x108)
                    localpos3 = self.handle.read_float((entity + self.m_vecOrigin + 0x8))  # + self.handle.read_float(vecorigin + self.m_vecViewOffset + 0x10C)
                    self.bomb_location = [localpos1, localpos2, localpos3]
                    print("bomb_location [on man]", self.bomb_location)
                    return [localpos1, localpos2, localpos3]
        print("bomb_location [planted]", self.bomb_location)
        return self.bomb_location


    def is_bomb_planted(self):
        GameRulesProxy = self.handle.read_uint(self.client_dll + self.dwGameRulesProxy)
        status = self.handle.read_uint(GameRulesProxy + self.m_bBombPlanted)
        if status == 0:
            return 0
        elif status == 1:
            return 1
        else:
            return 0
    def get_rounds_played(self):
        GameRulesProxy = self.handle.read_uint(self.client_dll + self.dwGameRulesProxy)
        rounds = self.handle.read_uint(GameRulesProxy + 0x64)

        return rounds
    def crosshair_id(self):
        local_player = self.handle.read_uint(self.client_dll + self.dwLocalPlayer)
        id = self.handle.read_uint(local_player + self.m_iCrosshairId)
        return id
    def shoot(self):
        # self.instant_stop()
        enemy = self.seeing_enemy()[0:3]
        if self.get_bullets(10) < 3:
            self.handle.write_int(self.client_dll + self.dwForceReload, 1)
            time.sleep(0.05)
            self.handle.write_int(self.client_dll + self.dwForceReload, 0)

        if len(enemy) != 0:
            # 如果在准星里 射击
            self.set_aim_to(enemy, smooth=3.7) #3.7
            if self.crosshair_id():
                print("shoot enemy", enemy)
                self.set_attack(6)


if __name__ == '__main__':
    handle = CSAPI(r"D:\PROJECT\BOT\api\csgo.json")

    #
    while True:
        # print(handle.set_walk([1,0,0,0,0,0]))
        # handle.set_walk_to([3300.9967857142856, 285.16, 0], [handle.shoot])
        # handle.set_aim_to([680.9183349609375, 1590.7235107421875, 1740.15966796875])
        # print(handle.seeing_enemy())
        en = handle.shoot()

        time.sleep(0.05)



