import struct

data = b'\x03\x00\x00\x00'

print(struct.unpack('<i', data))