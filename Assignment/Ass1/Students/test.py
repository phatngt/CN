from time import time
import sys
header = bytearray(12)
print(header)
version = 2
padding = 1
seqnum = 200
timestamp = int(time())
header[1] = seqnum >> 8
header[2] = 40000 >> 8

print("{0:b}".format(int(time())))
header[3] = (timestamp >> 24) & 0xFF
header[4] = (timestamp >> 16) & 0xFF
header[5] = (timestamp >> 8) & 0xFF
header[6] = timestamp & 0xFF
print("{0:b},{1:b},{2:b},{3:b}".format(header[3],header[4],header[5],header[6]))