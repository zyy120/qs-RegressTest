#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/10/9 17:09
@ file: unpack.py
@ site: 
@ purpose: unpack into plain text
"""
from RunFast.Common.protocol import *


#   根据参数数据类型分类
class ProtocolClassify:
    #   协议号对应的回包处理函数 SCRoomSnapshot
    protocol_corresponding_function = {1000: [SCLogin, "OnLogin"],
                                       1001: [SCApplyToEnterRoom, "OnInformEnterRoom"],
                                       1002: [SCRoomSnapshot, "SCRoomSnapshot"],
                                       1003: [SCDesktopSnapshot, "SCDesktopSnapshot"],
                                       1010: [SCCreateRoom, "OnCreateRoom"],
                                       1999: [SCReconnect, "OnReconnect"],
                                       1005: [SCReadyForGame, "OnReady"],
                                       1007: [SCGameStart, "OnGameStart"],
                                       1008: [SCDissolveRoom, "OnInformDissolveRoom"],
                                       1009: [SCLeaveRoom, "OnLeaveRoom"],
                                       1012: [SCAgreeDissolve, "OnVoteDissolveRoom"],
                                       1013: [SCDissolveReason, "OnDissolveReason"],
                                       2520: [SCReceiveCards, "OnRecvCards"],
                                       1021: [SCInformPlayerToDo, "OnInformPlayerToDo"],
                                       1022: [SCPlayerCanDo, "OnPlayerCanDo"],
                                       2523: [SCPlayerOperate, "OnPlayerOperate"],
                                       2531: [SCSettlement, "OnSettlement"],
                                       2535: [SCTotalSettlement, "OnTotalSettlement"],
                                       4999: [SCOffline, "OnOffline"],
                                       }


class UnPackData:
    #   初始化协议号及包体数据
    def __init__(self):
        self.current_index = 0
        self.result = None
        self.normal_entity_list = [1000, 1001, 1010, 1999, 1005, 1007, 5009, 1012, 1013, 1021, 4999,1087]

    def read_int16(self, data):
        value = struct.unpack("<h", data[0: 2])[0]
        return value

    def read_int32(self, data):
        value = struct.unpack("<i", data[0: 4])[0]
        return value

    def read_int64(self, data):
        value = struct.unpack("<q", data[0: 8])[0]
        return value

    def read_string(self, size, data):
        fmt = "<%ds" % size
        value = struct.unpack(fmt, data)[0]
        return value.decode("utf-8")

    def read_string1(self, data):
        size = self.read_int32()
        fmt = "<%ds" % size
        value = struct.unpack(fmt, self.body[self.cur_read_pos:self.cur_read_pos + struct.calcsize(fmt)])[0]
        return value

    def unpack_data(self, protocol_num, protocol_entity, data):
        need_parse_data = data
        entity = protocol_entity()
        entity_data = entity.sc_entity_data
        current_index = 0
        if protocol_num in self.normal_entity_list:
            for i in entity_data:
                if len(need_parse_data) <= 0 or len(need_parse_data) - current_index <= 0:
                    break

                if entity_data[i][0] == "INT32":
                    if len(need_parse_data) - current_index < 4:
                        break
                    entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                    current_index += 4

                elif entity_data[i][0] == "INT16":
                    if len(need_parse_data) - current_index < 2:
                        break
                    entity_data[i] = self.read_int16(need_parse_data[current_index: (current_index + 2)])
                    current_index += 2

                elif entity_data[i][0] == "INT64":
                    if len(need_parse_data) - current_index < 8:
                        break
                    entity_data[i] = self.read_int64(need_parse_data[current_index: (current_index + 8)])
                    current_index += 8
                else:
                    size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                    current_index += 4

                    entity_data[i] = self.read_string(size, need_parse_data[current_index: current_index + size])
                    current_index += size

        else:
            if protocol_num == 1008:  # 解散房间
                for i in entity_data:
                    if i == 'RoomDissolveInfo':
                        seat_id_list = {}
                        num = entity_data['RoomPlayers']
                        if num == 0:
                            break
                        for j in range(num):
                            if len(need_parse_data) - current_index < 4:
                                break
                            seat_id = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            IsAgree = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            seat_id_list["SeatID_%s" % seat_id] = seat_id
                            seat_id_list["IsAgree_%s" % seat_id] = IsAgree

                        entity_data[i] = seat_id_list

                    else:
                        if entity_data[i][0] == "INT32":
                            if len(need_parse_data) - current_index < 4:
                                break
                            entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4


            elif protocol_num == 2520:  # 发牌
                for i in entity_data:
                    if i == "CardsInfo":
                        num = entity_data['CardsNum']
                        if num == 0:
                            break
                        Cards = []
                        for j in range(num):
                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            card = self.read_string(size, need_parse_data[current_index: current_index + size])
                            current_index += size

                            Cards.append(card)

                        entity_data[i] = Cards

                    else:
                        if len(need_parse_data) - current_index < 4:
                            break
                        entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                        current_index += 4

            elif protocol_num == 1022:  # 通知用户做相应的操作
                for i in entity_data:
                    if i == "OperateInfo":
                        num = entity_data['OperateNum']
                        if num == 0:
                            break
                        operate_list = []
                        for j in range(num):
                            operate = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4
                            
                            null_str = self.read_string(size, need_parse_data[current_index: current_index + size])
                            current_index += size

                            operate_list.append(operate)
                        entity_data[i] = operate_list

                    else:
                        if entity_data[i][0] == "INT32":
                            entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4
                        else:
                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4
                            entity_data[i] = self.read_string(size,
                                                              need_parse_data[current_index: current_index + size])
                            current_index += size

            elif protocol_num == 2523:  # 出牌回包
                for i in entity_data:
                    if i == "Cards":
                        num = entity_data['CardNum']
                        if num == 0:
                            break
                        cards = []
                        for j in range(num):
                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4
                            card = self.read_string(size, need_parse_data[current_index: current_index + size])
                            current_index += size

                            cards.append(card)

                        entity_data[i] = cards

                    else:
                        if len(need_parse_data) - current_index < 4:
                            break
                        entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                        current_index += 4

            elif protocol_num == 2531:  # 小局结算
                for i in entity_data:
                    if i == "PlayerInfo":
                        num = entity_data['GamePlayers']
                        if num == 0:
                            break
                        player_info = {}
                        for j in range(num):
                            player_info[j] = {}
                            for info, _list in entity_data['PlayerInfo'][1].items():
                                if info == "Cards":
                                    num = player_info[j]['HandCardNum']

                                    hand_cards = []
                                    for w in range(num):
                                        size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                                        current_index += 4

                                        card = self.read_string(size, need_parse_data[current_index: current_index + size])
                                        current_index += size

                                        hand_cards.append(card)

                                    player_info[j][info] = hand_cards


                                elif info == "SendedCards":
                                    num = player_info[j]['SendedCardsNum']
                                    send_cards = []
                                    for z in range(num):
                                        size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                                        current_index += 4

                                        card = self.read_string(size,
                                                                need_parse_data[
                                                                current_index: current_index + size])
                                        current_index += size

                                        send_cards.append(card)

                                    player_info[j][info] = send_cards

                                else:
                                    if _list[0] == "INT32":
                                        player_info[j][info] = self.read_int32(
                                            need_parse_data[current_index: (current_index + 4)])
                                        current_index += 4

                                    elif _list[0] == "INT64":
                                        player_info[j][info] = self.read_int64(
                                            need_parse_data[current_index: (current_index + 8)])
                                        current_index += 8

                                    else:
                                        size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                                        current_index += 4

                                        player_info[j][info] = self.read_string(size, need_parse_data[current_index: current_index + size])
                                        current_index += size

                        entity_data[i] = player_info

                    elif i == "HoleCards":
                        num = entity_data['HoleCardNum']
                        if num == 0:
                            break
                        cards = []
                        for j in range(num):
                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            card = self.read_string(size,
                                                              need_parse_data[current_index: current_index + size])
                            current_index += size

                            cards.append(card)

                        entity_data[i] = cards


                    else:
                        if entity_data[i][0] == "INT32":
                            entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4
                        else:
                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            entity_data[i] = self.read_string(size,
                                                              need_parse_data[current_index: current_index + size])
                            current_index += size

            elif protocol_num == 2535:  # 总结算
                for i in entity_data:
                    if i == "PlayerInfo":
                        num = entity_data['GamePlayers']
                        if num == 0:
                            break

                        player_info = {}
                        for j in range(num):
                            player_info[j] = {}
                            for info, _list in entity_data['PlayerInfo'][1].items():
                                if _list[0] == "INT32":
                                    player_info[j][info] = self.read_int32(
                                        need_parse_data[current_index: (current_index + 4)])
                                    current_index += 4

                                elif _list[0] == "INT64":
                                    player_info[j][info] = self.read_int64(
                                        need_parse_data[current_index: (current_index + 8)])
                                    current_index += 8

                                else:
                                    size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                                    current_index += 4

                                    player_info[j][info] = self.read_string(size,
                                                                      need_parse_data[
                                                                      current_index: current_index + size])
                                    current_index += size

                        entity_data[i] = player_info

                    else:
                        if entity_data[i][0] == "INT32":
                            entity_data[i] = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4
                        else:
                            size = self.read_int32(need_parse_data[current_index: (current_index + 4)])
                            current_index += 4

                            entity_data[i] = self.read_string(size,
                                                              need_parse_data[current_index: current_index + size])
                            current_index += size

        self.result = entity_data
        return entity_data
