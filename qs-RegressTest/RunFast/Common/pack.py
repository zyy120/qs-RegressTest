#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ author: Hubery
@ create on: 2018/10/9 17:09
@ file: pack.py
@ site: 
@ purpose: packed into binary stream data
"""

import struct
import ctypes


class head:
    def __init__(self, cmd):
        self.flag = "QS"
        self.package_len = 0
        self.cmd = cmd

    def set_package_len(self, len):
        self.package_len = len

    def set_cmd(self, cmd):
        self.cmd = cmd

    def encode(self):
        format = '<%dshh' % len(self.flag)
        return struct.pack(format, self.flag.encode(), self.package_len, self.cmd)


class net_package:
    PACKAGE_HEAD_SIZE = 6
    PACKAGE_BUFFER_MAX_SIZE = 1024 * 4
    GOOD_PACKAGE_HEAD = 0
    COMPLETE_PACKAGE_BODY = 1
    UNCOMPLETE_PACKAGE_BODY = 2
    ERROR_INVALID_PACKAGE_HEAD = 3
    ERROR_TO_BIG_PACKAGE = 4

    def __init__(self, cmdid):
        self.body = b""  # ctypes.create_string_buffer(net_package.PACKAGE_BUFFER_MAX_SIZE - net_package.PACKAGE_HEAD_SIZE)
        self.package_len = 0
        self.cur_read_pos = 0
        # self.recvbuf_
        self.head = head(cmdid)
        self.data = None
        self.int32data = None

    def init_from_buff(self, buff):
        self.head.package_len = struct.unpack("<h", buff[2:4])[0]
        self.head.cmd = struct.unpack("<h", buff[4:6])[0]
        self.body = buff[net_package.PACKAGE_HEAD_SIZE:]
        self.cur_read_pos = 0

    def get_cmd(self):
        return self.head.cmd

    def write_int16(self, value):
        self.body += struct.pack("<h", value)
        self.package_len += struct.calcsize("<h")

    def write_int32(self, value):
        self.body += struct.pack("<i", value)

        self.int32data = struct.pack("<i", value)
        self.package_len += struct.calcsize("<i")

    def write_string(self, value):
        self.write_int32(len(value) + 1)
        format = '<%ds' % (len(value) + 1)
        self.data = struct.pack(format, value.encode())
        self.body += struct.pack(format, value.encode())
        self.package_len += struct.calcsize(format)

    def read_int16(self):
        fmt = "<h"
        value = struct.unpack(fmt, self.body[self.cur_read_pos: self.cur_read_pos + struct.calcsize(fmt)])[0]
        self.cur_read_pos += struct.calcsize(fmt)
        return value

    def read_int32(self):
        fmt = "<i"
        value = struct.unpack(fmt, self.body[self.cur_read_pos:self.cur_read_pos + struct.calcsize(fmt)])[0]
        self.cur_read_pos += struct.calcsize(fmt)
        return value

    def read_string(self):
        size = self.read_int32()
        fmt = "<%ds" % size
        value = struct.unpack(fmt, self.body[self.cur_read_pos:self.cur_read_pos + struct.calcsize(fmt)])[0]
        self.cur_read_pos += struct.calcsize(fmt)
        return value

    def encode(self):
        self.head.set_package_len(self.package_len)
        return self.head.encode() + self.body
