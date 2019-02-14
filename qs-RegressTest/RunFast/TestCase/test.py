import struct


def mains():
    # buffer= struct.pack("<i", 1)
    # s=struct.calcsize("<d")
    # b'QS`\x00\xf2\x03\x03\x00\x00\x0081\x00
    str = b'\x00\x0f'


    print(struct.unpack("<h", str))
if __name__ == '__main__':
    mains()
