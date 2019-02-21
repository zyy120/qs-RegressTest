#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/11/26 9:48
@ file: test_init.py
@ site: 
@ purpose: 
"""
import unittest
from RunFast.Common.api import *
class TestCaseLogin(unittest.TestCase):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_task(self):
        player_A = UserBehavior("Hubery_test1_93", isHomeOwner=True, isAuto=False)
        player_B = UserBehavior("Hubery_test2_94", isAuto=False)
        player_C = UserBehavior("Hubery_test3_95", isAuto=False)


        room_data = {"GameType": "81", "GameInnings": 6, "GamePaiNum": 16}
        player_A.CreateRoom(room_data)
        #if player_A.last_room_id is 0:
        # player_A.CreateRoom(room_data)
        # player_A.room_id = player_A.last_room_id

        cards_data = {
            "1": ["8s", "8h", "8c", "4s", "4h", "4c", "5s", "5h", "5c", "6s", "6h", "6c", "7s", "7h", "7c", "2s"],
            "2": ["Qd", "Ad", "Jc", "Th", "2s", "Ks", "9d", "3h", "7d", "Kc", "Jh", "Kh", "9c", "Jd", "9s", "8d"],
            "3": ["Qh", "4d", "3d", "Ac", "Js", "Tc", "Td", "Ts", "Qs", "Qc", "6d", "Ah", "9h", "3c", "5d", "Kd"]}


        player_A.MakeCards(cards_data)
        print("2222222222", player_A.room_id)
        time.sleep(2)
        while player_A.room_id == 0:
            time.sleep(1)

        time.sleep(2)

        print("房间ID: %s" % player_A.room_id)

        # time.sleep(10000)

        player_B.ApplyEnterRoom(player_A.room_id)
        player_C.ApplyEnterRoom(player_A.room_id)

        while not player_A.game_start:
            time.sleep(0.01)
        player_A.OperateApi("出",  ["8s", "8h", "8c", "4s", "4h", "4c", "5s", "5h", "5c", "6s", "6h", "6c", "7s", "7h", "7c"])
        player_B.OperateApi("过")
        player_C.OperateApi("过")
        player_A.OperateApi("出", ["2s"])
        time.sleep(5)
        # while not player_A.game_start:
        #     time.sleep(1)
        #
        # while not player_A.game_over:
        #     time.sleep(1)
        #
        # while not player_B.game_over:
        #     time.sleep(1)
        #
        # while not player_C.game_over:
        #     time.sleep(1)

        Round = player_A.big_round

        print("跑得快十五张三人玩法当前大局: %s" % (Round))

        print("所有用例结束")
        player_A.ConnectClose()
        player_B.ConnectClose()
        player_C.ConnectClose()



if __name__ == '__main__':
    unittest.main()