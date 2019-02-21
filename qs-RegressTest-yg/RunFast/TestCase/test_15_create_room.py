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

        while Round < 20:

            player_A = UserBehavior("Hubery_test_93", isHomeOwner=True)
            player_B = UserBehavior("Hubery_test_94")
            player_C = UserBehavior("Hubery_test_95")

            if Round % 2 == 0:
                print("1111111111")
                room_data = {"GameInnings": 10, "GamePlayOptions": 286}
                player_A.CreateRoom(room_data)

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