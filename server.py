#!/usr/bin/python3
import sys
import os
import socket
from socket import error as SocketError
import errno
import time
#from contextlib import suppress
import traceback
import struct

import routines

class Logger():
    def __init__(self,fullPath):
        self.fpath=fullPath
    def __call__(self,s):
        with open(self.fpath,"ab") as fso:
            s=time.strftime("%H:%M:%S -- %Y-%m-%d: ")+s
            s+="\n"
            s=s.encode()
            fso.write(s)
    def tb(self):
        with open(self.fpath,"a") as fso:
            (trash0,trash1,thetb)=sys.exc_info()
            traceback.print_tb(thetb, file = fso)
    def append(self,s):
        with open(self.fpath,"ab") as fso:
            s=s.encode()
            fso.write(s)

class RemoteSocketClosed(Exception):
    pass
    
class OrderedToClose(Exception):
    pass

def main(wdir):
    key=b"asdf"
    sendRoutines, responseRoutines = routines.initRoutines(key)
    
    wlog=Logger(os.path.join(wdir,"log.txt"))
    try:
        ServerSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSocket.bind(("192.168.43.96",55556))#"127.0.0.1"
        ServerSocket.listen(0)
        while True:
            try:
                (connectionSocket,address)=ServerSocket.accept()
                connectionSocket.settimeout(30)
                wlog.append("\n\n")
                wlog("connection to {} opened.".format(address))
                bInd=0
                bLen=0
                buff=b""
                mtype=None
                mlen=None
                headerRecieved=False
                while True:
                    if not headerRecieved:
                        if bLen-bInd < 12:
                            chunk=connectionSocket.recv(4096)
                            if len(chunk)==0:
                                raise RemoteSocketClosed
                            bLen+=len(chunk)
                            buff+=chunk
                            continue
                        if buff[bInd:bInd+4]==key:
                            
                            mtype, mlen = struct.unpack("<LL",buff[bInd+4:bInd+12])
                            bInd+=12
                            headerRecieved=True
                        else:
                            print(1,"error")
                            bInd+=1
                    if headerRecieved:
                        if bLen-bInd < mlen:
                            chunk=connectionSocket.recv(4096)
                            if len(chunk)==0:
                                raise RemoteSocketClosed
                            bLen+=len(chunk)
                            buff+=chunk
                            continue
                        else:
                            if mtype > len(responseRoutines)-1:
                                raise ValueError("there is no message type "+str(mtype))
                            print("messageCode: "+str(mtype)+"\nMessage: "+buff[bInd:bInd+mlen].decode())
                            responseRoutines[mtype](buff[bInd:bInd+mlen],connectionSocket)
                            buff=buff[bInd+mlen:]
                            bInd=0
                            bLen=len(buff)
                            headerRecieved=False
            except RemoteSocketClosed:
                connectionSocket.shutdown(socket.SHUT_RDWR)
                connectionSocket.close()
                print("connection closed by remote socket")
            except socket.timeout:
                connectionSocket.shutdown(socket.SHUT_RDWR)
                connectionSocket.close()
                print("connection timed out")
    except Exception as e:
        wlog("Server closing on Error: "+str(type(e))+" "+str(e))
        wlog.tb()
        connectionSocket.shutdown(socket.SHUT_RDWR)
        connectionSocket.close()
        ServerSocket.shutdown(socket.SHUT_RDWR)
        ServerSocket.close()
        print(9,buff)
        raise e


if __name__=="__main__":
    spath=__file__ #"/home/mr/RPiProject/dummy.py"
    path=os.path.dirname(spath)
    os.chdir(path)
    main(path)

