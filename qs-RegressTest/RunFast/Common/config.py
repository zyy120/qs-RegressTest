#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/10/9 16:56
@ file: config.py
@ site: 
@ purpose: server configuration, player configuration, php interface
"""
#   跑得快本地  # /home/user_00/dtz   # /home/user_01/beard/dtz_debug
SERVER_CONFIG_LOCAL = dict(site_id=2, channel_id=2024, gp_id=101, server_ip="192.168.1.152", server_port=9007)

#   跑得快测试服
SERVER_CONFIG_TEST = dict(site_id=2, channel_id=2024, gp_id=101, server_ip="118.178.135.235", server_port=10001)


#   跑得快本地php接口
local_bread_base_url = "http://192.168.1.111:81/beard/api/mobile/api.php?api="

#   跑得快测试服php接口
test_server_base_url = "http://testpay.jiaheyx.com/beard/api/mobile/api.php?api="


# 余干跑得快本地配置

beard_key="D9%J@#$A$%#@JA&&635"
SERVER_CONFIG = dict(site_id="2", channel_id="3000", gp_id="102", type="0", deviceid="684E9421-3D86-45A6-A332-CCC905C82A52",
                     server_ip="192.168.1.27", server_port=9130)
load_bread_url = "http://127.0.0.1:8080/app/api/"