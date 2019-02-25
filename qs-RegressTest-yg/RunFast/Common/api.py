#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/11/8 14:04
@ file: api.py
@ site: 
@ purpose: 
"""
import json
import copy
import requests
import random
import logging
import itertools
import hashlib
from collections import Counter
from RunFast.Common.config import *
from RunFast.Common.connect import *
from RunFast.Common.unpack import *
from RunFast.Common.protocol import *


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

InsignificantProtocolList = [
    1086,
    9999,
    10022,
    10080,
    1002,
    1004,
    11000,
    1003,
    #1005,   # 服务端广播进入房间的玩家信息
    5002,   # 服务器通知进入房间，房间快照
    5003,   # 服务器推送桌面快照
    5006,   # 服务器广播玩家重连
    5999,   # 暂离
    5026,   # 发送玩家桌面数据
    5028,   # 服务器广播炸弹结算
    1087,   #获取房卡数
    1105,
1006,2532,1088,1594,2025,2550,
]

AutoTestRound = 1
Any_Play_Card_Type = 1
Specify_Card_Type = 2
CONNECT_CLOSE_TIMEOUT = 60


def GetOperateID(_type):
    operate = None
    if _type == "过":
        operate = 1
    elif _type == "出":
        operate = 2
    else:
        print("暂未做此操作ID接口, 请说明该操作应用于哪个玩法, 进行添加!")
    return operate


class UserBehavior(object):
    def __init__(self, account, isHomeOwner=False, isAuto=False):
        self.homeowner = isHomeOwner            # 是否房主
        self.auto_test = isAuto                 # 是否自动打牌
        self.account = account                  # 昵称
        self.conn = None                        # socket连接对象
        self.sesskey = None                     # sesskey
        self.user_mid = None                    # 用户mid
        self.user_gp = None                     # 用户组
        self.players = None                     # 玩家人数
        self.room_id = 0                        # 房间ID
        self.seat_id = 0                        # 座位号
        self.last_room_id = 0                   # 上次房间号，判断断线重连之后是否在房间中
        self.hand_cards = []                    # 手牌
        self.remain_card_num = -1               # 牌墩剩余牌数
        self.room_type = None                   # 房间类型
        self.current_sequence = None            # 当前操作序列号
        self.last_player_operate_cards = None   # 上家出的牌
        self.last_player_seat_id = None         # 上家出牌的座位号
        self.players_remain_card_info = {}      # 上家手牌剩余数
        self.game_start = False                 # 游戏开始状态
        self.current_round = 0                  # 当前局数
        self.big_round = 0                      # 当前大局
        self.game_over = False                  # 游戏结束
        self.first_send_cards = True            # 游戏刚开始必须出黑桃三
        self.current_protocol_num_info = {}     # 记住当前的协议号，用于停止socket链接
        self.monitor_thread = None              # 监控数据线程
        self.CanOperate = False
        self.BasicTask()

    def BasicTask(self):
        self.GetUserSesskey()
        self.LoadUserInfo()
        self.ConnectGameServer()

    def GetUserSesskey(self):
        headers = {'content-type': "application/json"}
        try:
            params = "channel=%s&deviceid=%s&gp=%s&signCode=%s&site=%s&sitemid=%s&type=%s" % (
                SERVER_CONFIG['channel_id'], SERVER_CONFIG['deviceid'], SERVER_CONFIG['gp_id'], str(int(time.time())),
                SERVER_CONFIG['site_id'], self.account, SERVER_CONFIG['type'])
            sign = self.EncryptMD5(params + "&key=" + beard_key)
            params = params + "&sign=" + sign
            url = load_bread_url+"/login.do?" + params
            logging.debug("登陆java login url"+url)
            content = requests.post(url, headers=headers)
            data = json.loads(content.text)
            self.sesskey = data['data']['sesskey']
            if self.sesskey is None:
                logging.info("get sesskey is error.")
        except Exception as e:
            logging.info("GetUserSesskey", e)

    def LoadUserInfo(self):
        getUserData = {'sesskey': self.sesskey, 'signCode': str(int(time.time()))}
        try:
            params = "sesskey=%s&signCode=%s" % ( getUserData['sesskey'], str(int(time.time())))
            sign = self.EncryptMD5(params + "&key=" + beard_key)
            getUserData["sign"] = sign
            content = requests.post(load_bread_url+"load.do", getUserData)
            logging.info("get into java load.do pamram"+content.text)
            user_data = json.loads(content.text)
            self.user_mid, self.user_gp = user_data['data']['aUser']['mid'], user_data['data']['aUser']['gp']
            if self.user_mid is None or self.user_gp is None:
                logging.info("load user info is error by mid or gp is none.")
        except Exception as e:
            logging.info("LoadUserInfo", e)

    def ConnectGameServer(self):
        self.conn = Connecter(SERVER_CONFIG['server_ip'], SERVER_CONFIG['server_port'], self.ProtocolDataProcess,
                              self.ConnectSuccessCallBack)
        self.conn.async_connect()

    def ConnectSuccessCallBack(self):
        self.Login(self.user_mid, self.user_gp, self.sesskey)

    def ConnectClose(self):
        self.conn.connection_close()
        self.conn.close_loop()

    def SendDataToServer(self, data):
        self.conn.send_protocol(data)

    def ProtocolDataProcess(self, protocolNum, data):
        if protocolNum in InsignificantProtocolList:
            return

        # 处理包体数据，拿到明文数据，传递给各回包函数中处理
        logging.info("解析指令::%s"%(protocolNum))
        data_list = ProtocolClassify.protocol_corresponding_function[protocolNum]
        protocol_entity, funcName = data_list[0], data_list[1]
        real_data = UnPackData().unpack_data(protocolNum, protocol_entity, data)
        class_method = self.__class__.__dict__.get(funcName)
        #   协议处理
        if class_method:
            # 未登录状态在game server中执行登录前置要求
            class_method(self, real_data)
        else:
            logging.info(self.user_mid, "本类中不存在 <{0}> 方法".format(funcName))

    def EncryptMD5(self, data):
        h1 = hashlib.md5()
        h1.update(data.encode(encoding='utf-8'))
        return h1.hexdigest().upper()
##########################
### 登录
##########################
    def Login(self, mid, gp, sesskey):
        update_data = {"mid": mid, "gp": gp, 'sesskey': sesskey}
        cs_login_data = CSLogin(update_data)
        self.SendDataToServer(cs_login_data.real_data)

    def OnLogin(self, data):
        if data['ErrorCode'] is not 0:
            logging.info("玩家: {0} 登录失败, 错误码: {1}.".format(self.user_mid, data['ErrorCode']))
            return
        else:
            logging.info("玩家: {0} 登录成功.".format(self.user_mid))

    def OnReconnect(self, data):
        print("OnReconnect: %s" % data)
        if data['RoomID'] != 0:
            self.last_room_id = data['RoomID']
            print("断线重连在房间中，房间号: %s" % self.last_room_id)
            self.ApplyEnterRoom(data['RoomID'])
        else:
            logging.info("没有房间号.")

    def OnOffline(self, data):
        if  data['SeatID'] == self.seat_id:
            logging.info("房间通知: %s 号玩家掉线." % data['SeatID'])

##########################
### 房间操作
##########################
    def CheckIn(self):
        time.sleep(2)
        if self.last_room_id != 0 and self.homeowner:
            self.DissolveRoom()

        while self.last_room_id != 0:
            time.sleep(0.5)

    def CreateRoom(self, room_data):
        self.CheckIn()
        time.sleep(1)
        print("准备创建房间...")

        # room_data['GameClubID'] = 6721121
        # room_data['GameClubName'] = "自动化测试"
        data = CSCreateRoom(room_data)
        #print(data.real_data)
        self.SendDataToServer(data.real_data)

    def OnCreateRoom(self, data):
        print("OnCreateRoom: %s" % data)
        if data['ErrorCode'] is 0:
            self.room_id = data['RoomID']
            self.players = data['GamePlayers']
            logging.info("房间通知: 玩家%s 创建房间成功, 房间号: %s" % (self.user_mid, self.room_id))
        else:
            logging.info("房间通知: 玩家%s 创建房间失败, 错误码: %s" % (self.user_mid, data['ErrorCode']))

    def ApplyEnterRoom(self, room_id):
        room_data = {"RoomID": room_id, "EnterRoomType": 0}
        data = CSApplyToEnterRoom(room_data)
        self.SendDataToServer(data.real_data)

    def OnInformEnterRoom(self, data):
        print("OnInformEnterRoom: %s ,用户mid %s" % (data,self.user_mid))
        if data['SeatID'] >= 1:
            self.seat_id = data['SeatID']
            # if not self.homeowner:
            self.room_id = data['RoomID']
            logging.info("房间通知: 玩家%s进入房间%s, 座位号是: %s" % (self.user_mid, self.seat_id, self.seat_id))
            self.Ready()

        elif data['SeatID'] is -34:
            self.last_room_id = data['RoomID']

    def DissolveRoom(self):
        data = CSDissolveRoom()
        self.SendDataToServer(data.real_data)

    def OnInformDissolveRoom(self, data):
        print("OnInformDissolveRoom: %s" % data)
        if data['ErrorCode'] is 0 and self.seat_id != data['DismissSeatID']:
            if 0 in data['RoomDissolveInfo'].values():
                print("222222222")
                self.ToVoteDissolveRoom()

    def ToVoteDissolveRoom(self):
        data = CSAgreeDissolve()
        self.SendDataToServer(data.real_data)

    def OnVoteDissolveRoom(self, data):
        print("OnVoteDissolveRoom: %s" % data)
        if data['ErrorCode'] != 0:
            self.ToVoteDissolveRoom()
        else:
            logging.info("房间通知: 玩家%s 同意解散房间." % self.user_mid)

    def OnDissolveReason(self, data):
        self.last_room_id = 0
        logging.info("房间通知: 解散房间成功.")

    def ApplyLeaveRoom(self):
        data = CSLeaveRoom()
        self.SendDataToServer(data.real_data)

    def OnLeaveRoom(self, data):
        if data['SeatID'] == 1:
            self.last_room_id = 0

        if data['Mid'] == self.user_mid:
            if data['error_code'] == -17:
                logging.info("房间通知： 玩家: {0} 通过解散房间离开.".format(data['Mid']))
            else:
                logging.info("房间通知： 玩家: {0} 打完牌局后离开房间.".format(data['Mid']))

    def SCRoomSnapshot(self,data):
        logging.info("into SCRoomSnapshot")
        pass

    def SCDesktopSnapshot(self, data):
        logging.info("into SCDesktopSnapshot 指令：1003" )
        pass

        # 写牌推送
    def MakeCards(self, update_data):
         # str(update_data).replace("'", "\"")
        real_data = {"cards_list": str(update_data).replace("'", "\"")}

        cs_cards_type = CSMakeCardsType(real_data)
        print('make card data: %s' % cs_cards_type.real_data)
        self.SendDataToServer(cs_cards_type.real_data)

    ##########################
### 工具函数操作
##########################
    def ReplaceOpearate(self, _type):
        if _type == 0:
            return "过"
        elif _type == 1:
            return "可要"
        elif _type == 2:
            return "必须要"
        else:
            logging.info("服务端提醒操作协议有误. 提醒操作为: %s" % _type)

    def GetLastCardType(self, cards):
        reset_cards = set([card[0] for card in cards])
        print("查看上家牌型: %s, %s" % (reset_cards, len(reset_cards)))
        if len(cards) == 1:
            return "Single"
        elif len(cards) == 2:
            return "Pairs"
        elif len(cards) == 4:
            if len(reset_cards) == 1:
                return 'Bomb'
            else:
                return "CouplePairs"

        elif len(cards) == 5:
            if len(reset_cards) == 5:
                return "Straight"
            else:
                return "Triplet"
        else:
            return "Plane"


    def DivideCardType(self):
        all_card_type = {}
        hand_card = copy.deepcopy(self.hand_cards)

        #   获取单张、对子、连对、三条、飞机、炸弹等牌型
        reset_same_card = set([card[:1] for card in hand_card])
        for r_card in reset_same_card:
            r_card_list = [card for card in hand_card if r_card in card]
            if len(r_card_list) == 1:
                if "Single" not in all_card_type:
                    all_card_type["Single"] = []
                all_card_type["Single"].append(r_card_list)

            elif len(r_card_list) == 2:
                if "Pairs" not in all_card_type:
                    all_card_type["Pairs"] = []
                all_card_type["Pairs"].append(r_card_list)

            elif len(r_card_list) == 3:
                if "Triplet" not in all_card_type:
                    all_card_type["Triplet"] = []
                all_card_type["Triplet"].append(r_card_list)

            elif len(r_card_list) == 4:
                if "Bomb" not in all_card_type:
                    all_card_type["Bomb"] = []
                all_card_type["Bomb"].append(r_card_list)

            else:
                logging.info("当前同字牌型超过9张，牌型是: %s" % r_card_list)

        #   获取顺子
        reset_straight_list = list(itertools.combinations(set(hand_card), 5))
        for straight in reset_straight_list:
            cards  = sorted(self.ReplaceCardValue(list(straight)))
            if set(cards) == 5 and cards[-1] - cards[0] == 4:
                if "Straight" not in all_card_type:
                    all_card_type["Straight"] = []
                all_card_type["Straight"].append(list(straight))

        return all_card_type

    def ReplaceCardValue(self, cards):
        if type(cards) != list:
            cards = [cards]
        rep_cards = []
        for r_card in cards:
            if len(r_card) > 1:
                t_value = r_card[:1]
            else:
                t_value = r_card

           # print(cards, r_card, t_value)

            if t_value == "T":
                rep_cards.append(10)
            elif t_value == "J":
                rep_cards.append(11)
            elif t_value == "Q":
                rep_cards.append(12)
            elif t_value == "K":
                rep_cards.append(13)
            elif t_value == "A":
                rep_cards.append(14)
            elif t_value == "2":
                rep_cards.append(15)
            elif t_value == "L":# 小王
                rep_cards.append(16)
            elif t_value == "B":# 大王
                rep_cards.append(17)
            else:
                rep_cards.append(int(t_value))

        return rep_cards


    def GetSingle(self, _type, state, last_cards, all_card_type):
        print("玩家剩余牌情况: %s, 状态: %s" % (self.players_remain_card_info, state))
        s_cards = []

        #   获取玩家的下家牌数情况
        Just_One_Card_State = False
        for seat_id, card_num in self.players_remain_card_info.items():
            if self.seat_id != seat_id and card_num == 1:
                Just_One_Card_State = True

        #   如果下家只剩下一张牌
        if Just_One_Card_State:
                print("下家只剩下一张牌...")
                p_card = None
                #   如果是任意出牌
                if state == Any_Play_Card_Type:
                    p_card = self.ReplaceCardValue(['0c\x00'])
                #   如果是压上家牌
                elif state == Specify_Card_Type:
                    p_card = last_cards
                else:
                    logging.error("下家只剩下一张牌且选择单牌时, 传入状态错误，错误状态是: %s" % state)

                print("玩家手牌: %s" % self.hand_cards)

                #   如果手牌中不存在有炸弹，遍历手上最大的牌进行出牌
                if 'Bomb' not in all_card_type.keys():
                    print("没有炸弹")
                    #   手牌剩下一张不管是自由出牌还是压上家牌都是出最大的单牌
                    for index, h_x_card in enumerate(self.hand_cards):
                        h_card = copy.deepcopy(h_x_card)
                        print(index, last_cards, p_card, h_card)
                        if index == 0:
                            reset_card = self.ReplaceCardValue([h_card])
                            if reset_card[0] > p_card[0]:
                                p_card = h_x_card
                        else:
                            reset_card = self.ReplaceCardValue([h_card])
                            print("遍历手牌中最大的: %s, %s" % (reset_card, p_card), isinstance(p_card, str))
                            if isinstance(p_card, str):
                                value_card = self.ReplaceCardValue([p_card])
                                print("替换牌型<1>: %s" % value_card)
                            else:
                                value_card = p_card
                                print("替换牌型<2>: %s" % value_card)
                            if reset_card[0] > value_card[0]:
                                p_card = h_x_card

                    print("如果下家只有一张牌 ----  牌：%s" % p_card)
                    print(isinstance(p_card, list))
                    if isinstance(p_card, list):
                        s_cards = p_card
                    else:
                        s_cards.append(p_card)
                #   如果手牌中有炸弹的话，直接按着最大炸弹出牌
                else:
                    print("有炸弹, %s" % p_card)
                    reset_bomb = ['0cx\00']
                    for bomb in all_card_type['Bomb']:
                        reset_card = self.ReplaceCardValue([bomb[0]])
                        value_card = self.ReplaceCardValue([reset_bomb[0]])
                        if max(reset_card) >= max(value_card):
                            reset_bomb = bomb

                    print("有炸弹，选取的炸弹压单牌是: %s" % reset_bomb)
                    s_cards = reset_bomb
                logging.info("下家只剩下一张牌且选择单牌时，选择的单牌是: %s" % s_cards)

        #   如果下家不止一张牌
        else:
            p_card = None
            #   如果是任意出牌
            if state == Any_Play_Card_Type:
                p_card = self.ReplaceCardValue(['0c\x00'])
            #   如果是压上家牌
            elif state == Specify_Card_Type:
                p_card = last_cards
            else:
                logging.error("下家不止一张牌且选择单牌时, 传入状态错误，错误状态是: %s" % state)

            print("11111")

            #   获取炸弹的值, 用于炸弹不可拆玩法
            bomb_cards = []
            if 'Bomb' in all_card_type:
                for cards in all_card_type['Bomb']:
                    for card in cards:
                        bomb_cards.append(card)
                print("炸弹牌: %s, %s" % (bomb_cards, all_card_type['Bomb']))

            print("手牌: %s" % self.hand_cards)
            #   遍历找到手牌大于上家牌的牌选择压牌，或者任意出一张牌 <非炸弹>
            for h_x_card in self.hand_cards:
                h_card = copy.deepcopy(h_x_card)
                print("h_card: %s" % h_card)
                reset_card = self.ReplaceCardValue([h_card])
                print(reset_card[0], p_card[0], reset_card[0] >= p_card[0])
                if reset_card[0] > p_card[0] and h_card not in bomb_cards:
                    print("h_x_card： %s, p_card: %s" % (h_x_card, p_card))
                    p_card = h_x_card
                    break

            print("如果下家不止一张牌 ----  牌：%s" % p_card)

            #   说明没有取到可以压上家的牌型
            if p_card == last_cards:
                #   选取炸弹
                if len(bomb_cards) != 0:
                    s_cards = all_card_type['Bomb'][0]
            else:
                if isinstance(p_card, list):
                    s_cards = p_card
                else:
                    s_cards.append(p_card)

            logging.info("下家手牌不止一张且选择单牌时，选择的单牌是: %s" % s_cards)

        return s_cards

    def GetPairs(self, _type, last_cards, all_card_type):
        s_cards = []
        if 'Pairs' in all_card_type and  len(all_card_type['Pairs']) >= 1:
            for card in all_card_type['Pairs']:
                current_data = self.ReplaceCardValue(card)
                print("current_data: %s" % current_data)
                if max(current_data) > max(last_cards):
                    s_cards = card
                    break

        if len(s_cards) == 0:
            value_hand_card = [card[:1] for card in self.hand_cards]
            reset_card = set(value_hand_card)
            print("reset_card: %s, value_hand_card: %s" % (reset_card, value_hand_card))
            for card in list(reset_card):
                print("xxxxxxxxx", card, value_hand_card.count(card), type(value_hand_card.count(card)))
                if 2 <= value_hand_card.count(card) < 4:
                    value = self.ReplaceCardValue([card])
                    print(value, type(value), last_cards, type(last_cards), max(last_cards))
                    if max(self.ReplaceCardValue([card])) > max(last_cards):
                        index = 0
                        for h_card in self.hand_cards:
                            if card in h_card and index < 2:
                                s_cards.append(h_card)
                                index += 1
                            if index == 2:
                                break
                        if index == 2:
                            break
                if len(s_cards) == 5:
                    break
            print("对子: %s" % s_cards)

        #   如果上述都还没有成功组到可出的对子牌型，找炸弹
        if len(s_cards) == 0:
            #   获取炸弹的值, 用于炸弹不可拆玩法
            bomb_cards = []
            if 'Bomb' in all_card_type:
                for cards in all_card_type['Bomb']:
                    for card in cards:
                        bomb_cards.append(card)
                print("对子炸弹牌: %s, %s" % (bomb_cards, all_card_type['Bomb']))

            if len(bomb_cards) != 0:
                s_cards = all_card_type['Bomb'][0]

        return s_cards

    def GetCouplePairs(self, _type, last_cards, all_card_type):
        #   获取连对
        s_cards = []
        r_cards = sorted(self.ReplaceCardValue([cards[0] for cards in all_card_type['CouplePairs']]))

        l_data = list(set(last_cards))
        l_value = [d for d in l_data if last_cards.count(d) == 2]
        max_value, triplet_len, remain_len = max(l_value), len(l_value), (len(last_cards) - len(l_value) * 2)

        for index, card in enumerate(r_cards):
            flag = index + triplet_len - 1
            if flag <= len(r_cards) - 1:
                if r_cards[flag] - card == triplet_len - 1:
                    for i in range(flag + 1):
                        for cards in all_card_type['CouplePairs']:
                            if r_cards[i] in self.ReplaceCardValue([card[:1] for card in cards]):
                                s_cards.extend(cards)
        return s_cards

    def GetTriplet(self, _type, last_cards, all_card_type):
        s_cards = []
        #   三带一的三条值
        top_value = Counter(last_cards).most_common(1)[0][0]
        for card in all_card_type['Triplet']:
            current_data = self.ReplaceCardValue(card)
            print(max(current_data), top_value, max(current_data) > top_value)
            if max(current_data) > top_value:
                s_cards = card
                break

        print("三带二: %s" % s_cards)

        #   获取炸弹的值, 用于炸弹不可拆玩法
        bomb_cards = []
        if 'Bomb' in all_card_type:
            for cards in all_card_type['Bomb']:
                for card in cards:
                    bomb_cards.append(card)
            print("炸弹牌: %s, %s" % (bomb_cards, all_card_type['Bomb']))

        if len(s_cards) == 0 and len(bomb_cards) != 0:
            s_cards = all_card_type['Bomb'][0]
            return s_cards

        #   如果是三带一或者三带二, 需要找一个对子，或者两个单牌
        last_card_len = len(last_cards)
        if last_card_len != 3:
            need_num = last_card_len - 3
            for card in sorted(self.hand_cards):
                if need_num > 0 and card not in bomb_cards and card not in s_cards:
                    s_cards.append(card)
                    need_num -= 1

        return s_cards


    def GetPlane(self, _type, last_cards, all_card_type):
        #   获取三张
        s_cards = []
        r_cards = sorted(self.ReplaceCardValue([cards[0] for cards in all_card_type['Triplet']]))

        l_data = list(set(last_cards))
        l_value = [d for d in l_data if last_cards.count(d) == 3]
        max_value, triplet_len, remain_len = max(l_value), len(l_value), (len(last_cards) - len(l_value) * 3)

        for index, card in enumerate(r_cards):
            flag = index + triplet_len - 1
            if flag <= len(r_cards) - 1:
                if r_cards[flag] - card == triplet_len - 1:
                    for i in range(flag + 1):
                        for cards in all_card_type['Triplet']:
                            if r_cards[i] in self.ReplaceCardValue([card[:1] for card in cards]):
                                s_cards.extend(cards)

        #   获取带的牌
        if remain_len != 0:
            single_card_len = sum([len(cards) for cards in all_card_type['Single']])
            pairs_card_len = sum([len(cards) for cards in all_card_type['Pairs']])
            #   全部都是单牌
            if single_card_len >= remain_len:
                for i in range(remain_len):
                    s_cards.append(all_card_type['Single'][i][0])
                return

            #   全部用对子
            if pairs_card_len >= remain_len:
                while remain_len > 0:
                    for cards in all_card_type['Pairs']:
                        for card in cards:
                            s_cards.append(card)
                            remain_len -= 1
                            if remain_len <= 0:
                                break
                        if remain_len <= 0:
                            break
                return

            #   用对子也用单牌
            if (single_card_len + pairs_card_len) >= remain_len:
                for i in range(single_card_len):
                    s_cards.append(all_card_type['Single'][i][0])
                    remain_len -= 0

                while remain_len > 0:
                    for cards in all_card_type['Pairs']:
                        for card in cards:
                            s_cards.append(card)
                            remain_len -= 1
                            if remain_len <= 0:
                                break
                        if remain_len <= 0:
                            break
                return

        return s_cards

    def GetBomb(self, _type, last_cards, all_card_type):
        s_cards = []
        for card in all_card_type['Bomb']:
            current_data = self.ReplaceCardValue(card)
            if max(current_data) > max(last_cards) :
                s_cards = card
                break
        return s_cards

    def Dispatch(self, _type, state, last_cards, all_card_type):
        switcher = {
            "Single": self.GetSingle,
            "Pairs": self.GetPairs,
            "CouplePairs": self.GetCouplePairs,
            "Triplet": self.GetTriplet,
            "Plane": self.GetPlane,
            "Bomb": self.GetBomb,
        }

        try:
            print("switcher", _type)
            if _type == "Single":
                return switcher[_type](_type, state, last_cards, all_card_type)
            else:
                return switcher[_type](_type, last_cards, all_card_type)

        except Exception as e:
            logging.info("没有此玩法--> %s, 查看当前玩法名字是否正确." % _type)


    #   新一轮任意出牌
    def AnyPlay(self, _type, all_card_type):
        print("任意出牌选择的牌型: %s" % _type)
        s_cards = []
        #   获取随意牌型
        if _type == "Single":
            print("当前的座位号是: %s, 其他玩家剩余牌情况: %s" % (self.seat_id, self.players_remain_card_info))
            s_cards = self.GetSingle(_type, Any_Play_Card_Type, [0], all_card_type)

        elif _type == "Triplet":
            s_cards = all_card_type['Triplet'][0]
            if len(self.hand_cards) < 4:
                s_cards.remove(s_cards[0])

            elif len(self.hand_cards) == 4:
                #   如果单牌够用, 先清除单牌
                if "Pairs" in all_card_type and len(all_card_type['Pairs']) >= 1:
                    s_cards.append(all_card_type['Pairs'][0][0])
            else:
                #   如果单牌够用, 先清除单牌
                if "Single" in all_card_type and len(all_card_type['Single']) >= 2:
                    s_cards.append(all_card_type['Single'][0][0])
                    s_cards.append(all_card_type['Single'][1][0])
                #   单牌不够用, 则直接用对子
                elif "Pairs" in all_card_type and len(all_card_type['Pairs']) >= 1:
                    for card in all_card_type['Pairs'][0]:
                        s_cards.append(card)
                #   特殊情况，剩下只有两个飞机的三条, 改出对子
                else:
                    s_cards.remove(s_cards[0])

        elif _type == "Plane":
            s_cards = all_card_type['Plane'][0]
            remain_len = int(len(s_cards) / 3)
            #   获取带的牌
            if remain_len != 0:
                single_card_len = sum([len(cards) for cards in all_card_type['Single']])
                pairs_card_len = sum([len(cards) for cards in all_card_type['Pairs']])
                #   全部都是单牌
                if single_card_len >= remain_len:
                    for i in range(remain_len):
                        s_cards.append(all_card_type['Single'][i][0])
                    return

                #   全部用对子
                if pairs_card_len >= remain_len:
                    while remain_len > 0:
                        for cards in all_card_type['Pairs']:
                            for card in cards:
                                s_cards.append(card)
                                remain_len -= 1
                                if remain_len <= 0:
                                    break
                            if remain_len <= 0:
                                break
                    return

                #   用对子也用单牌
                if (single_card_len + pairs_card_len) >= remain_len:
                    for i in range(single_card_len):
                        s_cards.append(all_card_type['Single'][i][0])
                        remain_len -= 0

                    while remain_len > 0:
                        for cards in all_card_type['Pairs']:
                            for card in cards:
                                s_cards.append(card)
                                remain_len -= 1
                                if remain_len <= 0:
                                    break
                            if remain_len <= 0:
                                break
                    return

        else:
            if _type is not None and all_card_type is not None:
                s_cards = all_card_type[_type][0]

        return s_cards

    #   压上一家牌, 对应牌型
    def SpecifyCardType(self, _type, last_cards, all_card_type):
        s_cards = []
        print("压上家牌", _type, last_cards, all_card_type)
        #   如果上家压得牌型在手牌中选好的牌型中是有的话
        if _type in all_card_type.keys() and len(all_card_type[_type]) >= 1:
            s_cards = self.Dispatch(_type, Specify_Card_Type, last_cards, all_card_type)
            print("<1>压上家牌: %s" % s_cards)

        #   如果上家牌不在固有牌型中.
        else:
            if _type == "Single":
                s_cards = self.GetSingle(_type, Specify_Card_Type, last_cards, all_card_type)
            elif _type == "Pairs":
                s_cards = self.GetPairs(_type, last_cards, all_card_type)

            if len(s_cards) <= 0 and 'Bomb' in all_card_type and len(all_card_type['Bomb']) >= 1:
                s_cards = all_card_type['Bomb'][0]

            print("<2>压上家牌: %s" % s_cards)

        return s_cards

    #   出牌规则逻辑, 符合真实用户
    def GetCardType(self, operate_type):
        s_cards = []
        all_card_type = self.DivideCardType()
        print("%s 号玩家的所有牌型: %s" % (self.seat_id, all_card_type))
        print("上家座位号是: %s" % self.last_player_seat_id)
        # 必须出牌
        if 100 in operate_type:
            #   如果上家是自己出牌
            if self.last_player_seat_id == self.seat_id or self.last_player_operate_cards is None:
                logging.info("xxxxx")
                type_data = all_card_type.keys()
                _type = None
                if len(type_data) >= 1:
                    flag = random.randint(0, len(type_data) - 1)
                    for index, _d in enumerate(type_data):
                        if index == flag:
                            _type = _d

                #   任意出牌
                s_cards = self.AnyPlay(_type, all_card_type)
                print("任意出牌: %s" % s_cards)

            #   如果上家不是自己出牌
            else:
                logging.info("zzzzz")
                _type = self.GetLastCardType(self.last_player_operate_cards)

                print("上家牌： %s" % self.last_player_operate_cards)

                last_cards = self.ReplaceCardValue(self.last_player_operate_cards)
                print("_type: %s" % _type)

                #   选择对应牌型压上
                s_cards = self.SpecifyCardType(_type, last_cards, all_card_type)

                print("选择压上家的牌型是: %s" % s_cards)

        # 过牌
        elif 89 in operate_type:
            s_cards = []

        print()
        print()
        print()
        return s_cards

    def DelOutplayedCard(self, cards):
        logging.info("删除手牌 ---> 原本的手牌: %s，要删除的牌： %s" % (self.hand_cards, cards))
        for card in cards:
            if card in self.hand_cards:
                self.hand_cards.remove(card)
        logging.info("删除手牌 ---> 删除后的手牌: %s，要删除的牌： %s" % (self.hand_cards, cards))
        logging.info("")
        logging.info("")

    def ResetState(self):
        self.room_id = 0  # 房间ID
        self.seat_id = 0  # 座位号
        self.last_room_id = 0  # 上次房间号，判断断线重连之后是否在房间中
        self.hand_cards = []  # 手牌
        self.remain_card_num = -1  # 牌墩剩余牌数
        self.room_type = None  # 房间类型
        self.current_sequence = None  # 当前操作序列号
        self.last_player_operate_cards = None  # 上家出的牌
        self.last_player_seat_id = None  # 上家出牌的座位号
        self.game_start = False  # 游戏开始状态
        self.players_remain_card_info = {}
        self.first_send_cards = True
        self.current_round = 0  # 当前局数

    def ResetCurrentState(self):
        self.first_send_cards = True
        self.hand_cards = None
        self.current_sequence = None  # 当前操作序列号
        self.last_player_operate_cards = None  # 上家出的牌
        self.last_player_seat_id = None  # 上家出牌的座位号

##########################
### 打牌操作
##########################
    def Ready(self):
        data = CSReadyForGame()
        self.SendDataToServer(data.real_data)

    def OnReady(self, data):
        if data['SeatID'] == self.seat_id:
            logging.info("房间通知: %s 号玩家已准备完毕." % self.seat_id)

    def OnGameStart(self, data):
        print("OnGameStart: %s" % data)
        if data['ErrorCode'] == 0:
            logging.info("房间通知: 当前游戏处于第 %s 小局." % data['CurrentInnings'])
            self.current_round = data['CurrentInnings']
            self.game_start = True
            self.game_over = False

    def OnRecvCards(self, data):
        self.hand_cards = data['CardsInfo']
        logging.info("房间通知: 服务器发牌完毕. %s 号玩家手牌是: %s" % (self.seat_id, self.hand_cards))
        logging.info("")

    def OnInformPlayerToDo(self, data):
        if data['SeatID'] == self.seat_id:
            logging.info("房间通知: 当前小局: %s, 当前是%s 号玩家出牌轮次." % (self.current_round, data['SeatID']))

    def OnPlayerCanDo(self, data):
        if data['SeatID'] == self.seat_id:
            print("OnPlayerCanDo: %s" % data)
            logging.info("房间通知: %s 号玩家: %s" % (self.seat_id, data["OperateInfo"]))
            self.current_sequence = data['OperateSequence'][:len(data['OperateSequence']) - 1]
            self.CanOperate = True
            if self.auto_test and self.game_start:
                print("当前小局: %s" % self.current_round)
                #   如果是首局第一局，必须先出黑桃3
                if self.first_send_cards and self.current_round == 1:
                    if '3s\x00' in self.hand_cards:
                        self.first_send_cards = False
                        all_card_type = self.DivideCardType()
                        if 'Bomb' in all_card_type.keys() and len([bomb for bomb in all_card_type['Bomb'] if '3s\x00' in bomb]) >= 1:
                            cards = ['3s\x00', '3h\x00', '3c\x00', '3d\x00']
                        else:
                            cards = ['3s\x00']
                        logging.info("1111出牌的牌型是: %s" % cards)
                        self.PlayerOperate(cards)
                    else:
                        cards = self.GetCardType(data["OperateInfo"])
                        logging.info("2222出牌的牌型是: %s" % cards)
                        self.PlayerOperate(cards)
                    self.first_send_cards = False

                else:
                    cards = self.GetCardType(data["OperateInfo"])
                    logging.info("3333出牌的牌型是: %s" % cards)
                    self.PlayerOperate(cards)

    def PlayerOperate(self, cards):
        #str(cards).replace("'", "\"")
        operate_data = {"OperateSequence": self.current_sequence, "CardNum": len(cards), "Cards": cards}
        print(operate_data)
        data = CSPlayerOperate(operate_data)
        print("111111111111::: %s " % data.real_data)
        self.SendDataToServer(data.real_data)

    def PlayerOperateChow(self):
        pass

    def PlayerOperateChu(self):
        pass

    def PlayerOperateCancel(self):
        pass

    def OperateApi(self, option,card=""):
        print("card", card)

        while not self.CanOperate:
             time.sleep(0.01)

        operate = GetOperateID(option)

        if operate in [1, 2]:
            self.CanOperate = False
            self.PlayerOperate(card)
            self.current_sequence = None

    def OnPlayerOperate(self, data):
        logging.info("OnPlayerOperate 出牌： %s" % data)
        if data['SeatID'] < 0:
            return logging.info("%s号玩家出牌失败, 错误码: %s" % (self.seat_id, data['SeatID']))
        if data['SeatID'] == self.seat_id:
            # 是自己操作时, 删除手牌
            if data['CardNum'] == 0:
                logging.info("房间通知: 当前小局是: %s, %s号玩家的轮次，选择过." % (self.current_round, self.seat_id))
            else:
                logging.info("房间通知: 当前小局是: %s, %s号玩家的轮次，出牌: %s" % (self.current_round, self.seat_id, data['Cards']))
            self.DelOutplayedCard(data['Cards'])

        if data['CardNum'] != 0:
            #   记录上家出牌人的信息，座位号以及牌型
            self.last_player_seat_id = data['SeatID']
            self.last_player_operate_cards = data['Cards']

        if data['SeatID'] != self.seat_id:
            self.players_remain_card_info[data['SeatID']] = data['HandCardNum']


    def OnSettlement(self, data):
        if self.game_start:
            if self.seat_id - 1 in data['PlayerInfo'] and data['PlayerInfo'][self.seat_id - 1]['SeatID'] == self.seat_id:
                logging.info("房间通知: 当前小局: 第< %s >局, 剩余牌局: %s局,  %s 号玩家获取的分数是: %s" % (self.current_round, data['RemainInnings'], self.seat_id, data['PlayerInfo'][self.seat_id - 1]['SeatScore']))
                logging.info("")
                logging.info("=============-小局分隔符-==============")
                logging.info("")
                self.ResetCurrentState()
                time.sleep(2)
                self.Ready()



    def OnTotalSettlement(self, data):
        if self.game_start:
            self.big_round += 1
            if self.homeowner:
                msg = ""
                for i in range(len(data['PlayerInfo'])):
                    msg += '%s 号玩家总成绩: %s, ' % (data['PlayerInfo'][i]['SeatID'], data['PlayerInfo'][i]['SeatScore'])
                logging.info("房间通知: 当前大局: %s, 总结算信息: %s" % (self.big_round, msg))
            self.game_over = True
            #   重置所有参数
            self.ResetState()
            time.sleep(2)

