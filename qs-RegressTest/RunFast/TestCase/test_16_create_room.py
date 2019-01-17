#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/11/30 14:12
@ file: test_15_create_room.py
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

        Round = 0

        room_id = None

        while Round < 1:

            player_A = UserBehavior("Hubery_test_93", isHomeOwner=True)
            player_B = UserBehavior("Hubery_test_94")
            player_C = UserBehavior("Hubery_test_95")

            if Round % 2 == 0:
                print("1111111111")
                room_data = {"GameType": "81","GameInnings": 6,"GamePaiNum": 16}
                if player_A.last_room_id is 0:
                    player_A.CreateRoom(room_data)

                player_A.room_id = player_A.last_room_id
                print("2222222222")

                while not player_A.room_id:
                    time.sleep(1)

                print("房间ID: %s" % player_A.room_id)

                player_B.ApplyEnterRoom(player_A.room_id)
                player_C.ApplyEnterRoom(player_A.room_id)

            else:
                room_id = player_A.last_room_id
                player_A.ApplyEnterRoom(room_id)
                player_B.ApplyEnterRoom(room_id)
                player_C.ApplyEnterRoom(room_id)


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

            time.sleep(3)
            print()
            print()
            print()
            print()
            print()
            print()
            print()

            time.sleep(2)
            Round += 1
            print("当前是第 %s 次" % Round)




if __name__ == '__main__':
    unittest.main()