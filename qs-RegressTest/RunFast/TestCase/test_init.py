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
        player_A = UserBehavior("Hubery_test_93", isHomeOwner=True, isAuto=True)
        player_B = UserBehavior("Hubery_test_94", isAuto=True)
        player_C = UserBehavior("Hubery_test_95", isAuto=True)

        Round = 0
        while Round < AutoTestRound:
            room_data = {"GameType": "81", "GameInnings": 6, "GamePaiNum": 16}
            player_A.CreateRoom(room_data)
           #  if player_A.last_room_id is 0:
           #      player_A.CreateRoom(room_data)
            # player_A.room_id = player_A.last_room_id
            print("2222222222", player_A.room_id)
            while player_A.room_id == 0:
                time.sleep(1)

            time.sleep(2)

            print("房间ID: %s" % player_A.room_id)

            # time.sleep(10000)

            player_B.ApplyEnterRoom(player_A.room_id)
            player_C.ApplyEnterRoom(player_A.room_id)

            while not player_A.game_start:
                time.sleep(1)

            while not player_A.game_over:
                time.sleep(1)

            while not player_B.game_over:
                time.sleep(1)

            while not player_C.game_over:
                time.sleep(1)

            Round = player_A.big_round

            print("跑得快十五张三人玩法当前大局: %s" % (Round))

        print("所有用例结束")
        player_A.ConnectClose()
        player_B.ConnectClose()
        player_C.ConnectClose()



if __name__ == '__main__':
    unittest.main()