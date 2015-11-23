#!/usr/bin/python3

from select import select
import sys
import os

fp=os.ttyname(sys.stdin.fileno())
sys.stdin.close()
filen=os.open(fp, os.O_RDONLY | os.O_NONBLOCK)

try:
    while True:
        readyRead, readyWrite, excepts = select([filen],[],[],1.0)
        if len(readyRead):
            print("input is :", os.read(readyRead[0], 4096).decode())
        else:
            print("time")
except Exception as e:
    raise e
finally:
    os.close(filen)
