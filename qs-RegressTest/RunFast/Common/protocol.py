#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/11/8 14:03
@ file: protocol.py
@ site: 
@ purpose: 
"""
from RunFast.Common.pack import *


class Encrypt2ParseData:
    def __init__(self, update_data, method=None):
        self.update_data = update_data
        self.method = method

    #   Update protocol data and perform different processing of data according to requirements.
    def get_update_data(self):
        if self.method == "pack":
            return self.pack_data()
        elif self.method == "unpack":
            return self.unpack_data()
        else:
            return None

    #   pack data
    def pack_data(self):
        package = net_package(self.update_data["protocol_num"][1])

        if len(self.update_data) > 0:
            for k, v in self.update_data.items():
                if k != "protocol_num":
                    if v[0] == "INT32":
                        package.write_int32(v[1])
                    elif v[0] == "INT64":
                        package.write_int32(v[1])
                    elif v[0] == "INT16":
                        package.write_int16(v[1])
                    elif v[0] == "STRING":
                        if self.update_data["protocol_num"][1] == 2523:
                            if type(v[1]) == list:
                                for i in v[1]:
                                    package.write_string(i[: len(i) - 1])
                            else:
                                # print(u"单张出牌操作数据: %s" % str(v[1]))
                                package.write_string(str(v[1]))
                        else:
                            package.write_string(str(v[1]))
        # print("package.encode: %s" % package.encode())
        return package.encode()

    #   unpack data
    def unpack_data(self):
        pass

#   Update protocol data.
class CommonUtils2UpdateData:
    def __init__(self, original_data, original_data_keys_list, update_data, method):
        self.original_data = original_data
        self.original_data_keys_list = original_data_keys_list
        self.data = update_data
        self.method = method

    def update_data(self):
        if len(self.data) > 0:
            for k, v in self.data.items():
                if k in self.original_data_keys_list:
                    self.original_data[k][1] = v

        # print("data: %s" % self.original_data)
        ud = Encrypt2ParseData(self.original_data, self.method)
        return ud.get_update_data()


#   common api to call update data
class CallUpdateApi:
    def __init__(self, original_data, original_data_keys_list, update_data, method):
        self.original_data = original_data
        self.original_data_keys_list = original_data_keys_list
        self.update_data = update_data
        self.method = method
        self.real_data = None
        self.get_real_data()

    def get_real_data(self):
        cu = CommonUtils2UpdateData(self.original_data, self.original_data_keys_list, self.update_data, self.method)
        self.real_data = cu.update_data()

######################
### 登录
######################

#   login entity --> CS
class CSLogin:
    def __init__(self, data={}):
        self.cs_login_entity = {"protocol_num": ["INT32", 1000], "mid": ["INT32", 0], "sesskey": ["STRING", ""],
                                "gp": ["INT32", 0], "sid": ["INT32", 1500]}
        self.cs_keys_list = self.cs_login_entity.keys()
        self.update_data = data
        self.method = "pack"
        self.real_data = CallUpdateApi(self.cs_login_entity, self.cs_keys_list, self.update_data, self.method).real_data


#   login entity --> SC
class SCLogin:
    def __init__(self, data={}):
        self.sc_entity_data = {"ErrorCode": ["INT32", 0], "UnUsed1": ["INT32", 100], "UnUsed2": ["INT32", 100]}
        self.sc_login_keys_list = self.sc_entity_data.keys()
        self.update_data = data
        self.method = "unpack"

class SCReconnect:
    def __init__(self):
        self.sc_entity_data = {"playType": ["INT32", 0],"RoomID": ["INT32", 0], "SID": ["INT32", -100]}
class SCOffline:
    def __init__(self):
        self.sc_entity_data = {"SeatID": ["INT32", 0]}

######################
### 房间内容
######################

#   创建房间 --1010
class CSCreateRoom():
    def __init__(self, data={}):
      self.entity = {
          "protocol_num": ["INT32", 1010],
          "GameType": ["STRING", "81"],  # 游戏类型
          "GameInnings": ["INT32", 0],  # 局数
          "GamePaiNum": ["INT32", 0],  #  牌的张数
          "GameFirstRule": ["INT32", 0],  #  首局规则
          "GameShouJu3cFirst": ["INT32", 0],  # 黑桃3首出规则 -- 0无要求 1 黑桃3先出
          "GameShowRest": ["INT32", 0],  # 显示剩余牌数
          "GameSelectWanFa1": ["INT32", 0],  #  多选1
          "GameSelectWanFa2": ["INT32", 0],  # 多选2
          "GamePlayers": ["INT32", 3],  # 人数 -- 几人(2,3,4)
          "GamePiao": ["INT32", 0],  # 飘
          "GameJoinGame": ["INT32", 0],  # 0普通创房 1代理开房 3茶馆
          "GameClunId": ["INT32", 0],  #
          "GamePaytype": ["INT32", 0],  #是否AA制开房，0否，1是
          "GameCoverCard": ["INT32", 0],  #是否首轮盖牌，0否，1是
          "GameClubName": ["STRING", ""],  #俱乐部名字，代理商名字
          "GameIsCreateEmptyRoom": ["INT32", 0],  # 俱乐部名字，代理商名字
          "GamePassWord": ["INT32", 0],  # 密码
          "GameFZB": ["INT32", 0],  # 防作弊
          "GameAgentDRoom": ["INT32", 0],  #  所有人同意解散
          "GameWanFaIndex": ["INT32", 0],  #  玩法下标
          "GameKoFangKa": ["INT32", 0],  # 是否使用自己房卡开房(0用自己的)
          "GameBaodi": ["INT32", 0],  # 报单是否保底 0保底 1不保底
          "GameIsGuanPai": ["INT32", 0],  # 关牌
      }
      self.cs_keys_list = self.entity.keys()
      self.update_data = data
      self.method = "pack"
      self.real_data = CallUpdateApi(self.entity, self.cs_keys_list, self.update_data, self.method).real_data


#   创建房间回包 --1010
class SCCreateRoom():
    def __init__(self):
        self.sc_entity_data = {
            "Type": ["INT32", 0],
            "ErrorCode": ["INT32", 0],
            "RoomID": ["INT32", 0],
            "RoomType": ["STRING", ""],
            "GameInnings": ["INT32", 0],
            "GamePlayers": ["INT32", 3],
            "GamePlayOptions": ["INT32", 0],
            "GameBaseScore": ["INT32", 0],
            "GameDouble": ["INT32", 0],  # 加倍
            "GameDoubleCondition": ["INT32", 0],
            "GameClubID": ["INT32", 0],
            "GameClubName": ["STRING", ""],
            "GameFixedPlay": ["INT32", 0],
            "GameFixedIndex": ["INT32", -1],
            "GameLimitIP": ["INT32", 0],
        }


#   申请加入房间 --1001
class CSApplyToEnterRoom:
    def __init__(self, data):
        self.entity = {
            "protocol_num": ["INT32", 1001],
            "RoomID": ["INT32", 0],         # 房间ID
            "Version": ["INT32", 0],        # 版本
            "NetWork": ["INT32", 0],        # 网络
            "PassWord": ["INT32", 0],       # 密码
            "Source": ["INT32", 0],         # 0:来自app，1:来自h5
            "ClubPay": ["INT32", 0]       # 0 普通 1代开 3俱乐部
        }
        self.cs_keys_list = self.entity.keys()
        self.update_data = data
        self.method = "pack"
        self.real_data = CallUpdateApi(self.entity, self.cs_keys_list, self.update_data,
                                       self.method).real_data

#   申请加入房间回包 --1001
class SCApplyToEnterRoom:
    def __init__(self):
        self.sc_entity_data = {
            "playType":["INT32", 0],
            "SeatID": ["INT32", 0],
            "RoomID": ["INT32", 0]
            #"RoomType": ["STRING", ""],
            #"RoomID": ["INT32", 0],
            #"GameFixedIndex": ["INT32", 0],
            #"GameClubID": ["INT32", 0],
            #"RoomState": ["INT32", 0]       # 房间状态(0:进入房间（等待开始） 1:游戏中 2:空闲状态)
        }

#   room snapshot 1002 快照   -->SC
class SCRoomSnapshot:
    def __init__(self):
        self.sc_entity_data = {"room_owner": ['INT32', 0], "room_state": ["INT32",0],"total_ju": ["INT32",0],"players_num": ["INT32",0],
                               "_player_info": ["INT32",{"seat_id": ['INT32', 0],"ip": ["STRING", ""], "mid": ['INT32', 0],"gp": ['INT32', 0],
                                                 "sex": ['INT32', 0], "name": ["STRING", ""],
                                                 "icon": ["STRING", ""], "city": ['STRING', 0],
                                                 "json_str": ["STRING", 0]}],
                               "banker_seatno": ["INT32", 0], "seats_size": ["INT32", 0], "banker_seatno": ["STRING", 0]}
#   desktop snapshot --> SC
class SCDesktopSnapshot:
    def __init__(self):
        self.sc_entity_data = {"room_num": ["INT32", 0], "room_type": ["STRING", ""], "total_times": ["INT32", 0],
                               "banker_seat_id": ["INT32", 0], "current_player_seat_id": ["INT32", 0],
                               "current_card": ["STRING", ""], "current_send_card_seat_id": ["INT32", 0],
                               "hupai_type": ["INT32", 0], "player_num": ["INT32", 0], "player_info": ["INT32", {
                "seat_id": ["INT32", 0], "mid": ["INT32", 0], "zanli": ["INT32", 0], "isready": ["INT32", 0],
                "huxi": ["INT32", 0], "send_card_num": ["INT32", 0], "_card_list": ["STRING", ""],
                "molding_card": ["INT32", 0], "_card_type_list": ["INT32", {"shoupai_type": ["INT32", 0],
                                                                            "card_num": ["INT32", 0],
                                                                            "_card": ["STRING", ""], }]}],
                               "homer_seat_id": ["INT32", 0], "game_start_type": ["INT32", 0],
                               "player_number": ["INT32", 0],
                               "_player": ["INT32", {"seat_id": ["INT32", 0], "jiatuo_daniao": ["STRING", ""]}]}

#   解散房间 --1008
class CSDissolveRoom:
    def __init__(self):
        self.entity = {"protocol_num": ["INT32", 1008]}
        self.cs_keys_list = self.entity.keys()
        self.update_data = {}
        self.method = "pack"
        self.real_data = CallUpdateApi(self.entity, self.cs_keys_list, self.update_data,
                                       self.method).real_data

#   解散房间回包 --1008
class SCDissolveRoom:
    def __init__(self):
        self.sc_entity_data = {
            "ErrorCode": ["INT32", -100],
            "DismissSeatID": ["INT32", 0],  # 申请解散座位ID
            "AutoAgreeDissolveTime": ["INT32", 0],  # 剩余自动解散时间
            "RoomPlayers": ["INT32", -100],
            "RoomDissolveInfo": [
                "INT32",
                {
                    "SeatID": ["INT32", -100],
                    "IsAgree": ["INT32", -100]
                }
            ]
        }

#   同意解散 --1012
class CSAgreeDissolve:
    def __init__(self):
        self.cs_club_game_list_data = {
            "protocol_num": ["INT32", 1012],
            "Agree": ["INT32", 1]
        }
        self.cs_keys_list = self.cs_club_game_list_data.keys()
        self.update_data = {}
        self.method = "pack"
        self.real_data = CallUpdateApi(self.cs_club_game_list_data, self.cs_keys_list, self.update_data,
                                       self.method).real_data

#   同意解散回包 --1012
class SCAgreeDissolve:
    def __init__(self):
        self.sc_entity_data = {"ErrorCode": ["INT32", -100]}

#   解散房间原因 --5013
class SCDissolveReason:
    def __init__(self):
        self.sc_entity_data = {"RoomId": ["INT32", -100], "RoomType": ["STRING", ""], "DissolveType": ["INT32", -100]}

#   申请离开房间 --5009
class CSLeaveRoom:
    def __init__(self):
        self.entity = {
            "protocol_num": ["INT32", 4009]
        }
        self.cs_keys_list = self.entity.keys()
        self.update_data = {}
        self.method = "pack"
        self.real_data = CallUpdateApi(self.entity, self.cs_keys_list, self.update_data,
                                       self.method).real_data

#   申请离开房间 --5009
class SCLeaveRoom:
    def __init__(self):
        self.sc_entity_data = {"Mid": ["INT32", 00], "SeatID": ["INT32", 99]}

##########################
### 开始牌局
##########################

#   准备 --1005
class CSReadyForGame:
    def __init__(self, data={}):
        self.entity = {"protocol_num": ["INT32", 1005]}
        self.cs_keys_list = self.entity.keys()
        self.update_data = data
        self.method = "pack"
        self.real_data = CallUpdateApi(self.entity, self.cs_keys_list, self.update_data,
                                       self.method).real_data

#   准备回包 --1005
class SCReadyForGame:
    def __init__(self):
        self.sc_entity_data = {"SeatID": ["INT32", 0]}


#   游戏开始回包 --1007
class SCGameStart:
    def __init__(self):
        self.sc_entity_data = {"ErrorCode": ["INT32", -100], "CurrentInnings":["INT32", 0]}


#   发牌回包 --2520
class SCReceiveCards:
    def __init__(self):
        self.sc_entity_data = {
            "CardsNum": ["INT32", 0],
            "CardsInfo": ["INT32", {"Card":["STRING", ""]}]
        }

#   通知玩家出牌 --1021
class SCInformPlayerToDo:
    def __init__(self):
        self.sc_entity_data = {
            "SeatID": ["INT32", 0],
            "OpSize": ["INT32", 0],
            "op": ["INT32", 0]
        }


#   通知用户做相应的操作回包 --1022
class SCPlayerCanDo:
    def __init__(self):
        self.sc_entity_data = {
            "SeatID": ["INT32", 0],
            "OperateNum": ["INT32", 0],
            "OperateInfo": ["INT32", -100], # 1 无效  89:过牌 100:出牌 104:取消
            "OperateSequence": ["STRING", ""],
            "NotByYao": ["INT32", 0]
        }


#   用户请求出牌 --2523
class CSPlayerOperate:
    def __init__(self, data={}):
        self.entity = {"protocol_num": ["INT32", 2523], "OperateSequence": ["STRING", ""], "CardNum": ["INT32", 0], "Cards": ["STRING", ""]}
        self.cs_keys_list = self.entity.keys()
        self.update_data = data
        self.method = "pack"
        self.real_data = CallUpdateApi(self.entity, self.cs_keys_list, self.update_data,
                                       self.method).real_data

#   用户请求回包 --2523
class SCPlayerOperate:
    def __init__(self):
        self.sc_entity_data = {
            # "ErrorCode": ["INT32", -100],
            "SeatID": ["INT32", -100],
            "HandCardNum": ["INT32", -100],  # 手牌数
            "CardNum": ["INT32", -100],
            "Cards": ["STRING", ""],
            #"IsAutoSendCard": ["INT32", -100],
        }



#   小局结算 --2531
class SCSettlement:
    def __init__(self):
        self.sc_entity_data = {
            "Type": ["INT32", -100],
            "BankerSeatID": ["INT32", -100],
            "RemainInnings": ["INT32", -100],
            "GamePlayers": ["INT32", -100],
            "PlayerInfo":["INT32",
                          {
                              "SeatID": ["INT32", -100],
                              "Mid": ["INT32", -100],
                              "Name": ["STRING", ""],
                              "Icon": ["STRING", ""],
                              "BombCount": ["INT32", -100],     # 炸弹次数
                              "CurrentScore": ["INT32", -100],  # 当局得分
                              #"SeatScore": ["INT64", -100],     # 座位分
                              "PiaoFenScore": ["INT32", 0],  #飘分得分
                              "PiaoFen": ["INT32", 0],  #是否飘分
                              "SeatScore": ["INT64", -100],  # 总分
                              "HandCardNum": ["INT32", -100],   # 手牌牌数
                              "Cards": ["STRING", ""],          # 牌
                          }
            ],
            "RoomInfo": ["STRING", ""],         # 房间信息
            "ZhongBirdSeatID": ["INT32", -100], # 中鸟座位号
            "ReservedParam": ["STRING", ""],    # 预留字段
        }

#   总结算 --2535
class SCTotalSettlement:
    def __init__(self):
        self.sc_entity_data = {
            "type": ["INT32", -100],
            "RoomOwner": ["INT32", -100],
            "GamePlayers": ["INT32", 0],
            "PlayerInfo": ["INT32",
                           {
                               "SeatID": ["INT32", -100],
                               "Mid": ["INT32", -100],
                               "Name": ["STRING", ""],
                               "Icon": ["STRING", ""],
                               "SeatScore": ["INT64", -100],  # 座位分
                               "BombCount": ["INT32", -100],  # 炸弹次数
                               "WinCount": ["INT32", -100],  # 赢得局数
                               "LoseCount": ["INT32", -100],  # 输的局数
                               "OneGameMaxScore": ["INT32", -100],  # 当局最高得分
                               "NSpringCount": ["INT32", -100] #被春天数

                           }
                           ],
            "RoomInfo": ["STRING", ""]
        }