import sys
import os
import socket
from socket import error as SocketError
import errno
import time
#from contextlib import suppress
import traceback
import struct
import ctypes
from collections import namedtuple

class RemoteSocketClosed(Exception):
    pass
    
class OrderedToClose(Exception):
    pass

def initRoutines(mkey):
    if type(mkey)!=type(b"bytes"):
        raise ValueError
        
    def receive(connection):
        mtype=None
        mlen=None
        header=b""
        message=b""
        gothb=0
        gotmb=0
        while True:
            if gothb< 12:
                chunk=connection.recv(12-gothb)
                if len(chunk)==0:
                    raise RemoteSocketClosed
                gothb+=len(chunk)
                header+=chunk
                continue
            if header[:4]==mkey:
                print("the header len:",len(header),"header:",header)
                mtype, mlen = struct.unpack("<LL",header[4:])
                break
            else:
                print("message starts with: {} which is not the mkey {}. Moving a byte forward.".format(header,mkey))
                header=header[:1]
                gothb=11
        while True:
            if gotmb< mlen:
                chunk=connection.recv(mlen-gotmb)
                if len(chunk)==0:
                    raise RemoteSocketClosed
                gotmb+=len(chunk)
                message+=chunk
            else:
                return mtype, message 
        
    #Response routines    
    def justPrint(binary, connection):
        print("justPrint response")
        print(binary.decode())

    def comeback(binary, connection):
        print("comeback response")
        binary= b"'"+binary+b"' right back at ya!"
        print(binary)
        connection.sendall(binary)
        
    def packetedComeback(binary, connection):
        print("packetedComeback response")
        binary= b"'"+binary+b"' right back at ya!" 
        mlen=len(binary)
        binary=mkey+ctypes.c_uint32(0)+ctypes.c_uint32(mlen)+binary
        print(binary)
        connection.sendall(binary)

    def toCommandPipe(binary, connection):
        print("acting on command",binary)
        with open("/tmp/commandPipe","w") as fso:
             fso.write(binary.decode())

    #Send routines    
    def toBePrinted(binary, connection):
        mlen=ctypes.c_uint32(len(binary))
        binary=mkey+ctypes.c_uint32(0)+mlen
        connection.sendall(binary)
        
    def toGetComeback(binary, connection):
        mlen=ctypes.c_uint32(len(binary))
        binary=mkey+ctypes.c_uint32(2)+mlen+binary
        print("sending:",binary)
        connection.sendall(binary)
        return receive(connection)[1]

    def toBeExecuted(binary, connection):
        mlen=ctypes.c_uint32(len(binary))
        binary=mkey+ctypes.c_uint32(3)+mlen+binary
        print("sending:",binary)
        connection.sendall(binary)


        
    sendNamedTuple=namedtuple("sendRoutines","toBePrinted toGetComeback toBeExecuted")
    responseNamedTuple=namedtuple("responseRoutines","justPrint comeback packetedComeback toCommandPipe")
    
    return (sendNamedTuple(toBePrinted, toGetComeback, toBeExecuted), 
            responseNamedTuple(justPrint, comeback, packetedComeback, toCommandPipe))

