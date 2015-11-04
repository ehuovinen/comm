import sys
import os
import socket
from socket import error as SocketError
import errno
import time
import traceback
import struct
import ctypes

import routines
def startConnection():
     holder=SocketCommunication()
     holder.specify_information("192.168.43.96","sadf","asdf")
     holder.connect()
     return holder

class SocketCommunication():
    def __init__(self):
        pass
    
    def specify_information(self, host, username, password, mkey=b"asdf"):
        self.host=host
        self.hostPort=55556
        self.username=username
        self.password=password
        self.ssh=None
        self.timeout=5
        self.sendRoutines, self.receiveRoutines=routines.initRoutines(mkey)
        
    def connect(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((self.host, self.hostPort))
        self.socket.settimeout(self.timeout)
        self.disconnect()

        
    def disconnect(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        
    def command(self, command):

        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((self.host, self.hostPort))
        self.socket.settimeout(self.timeout)

        command=command.encode()
        rv=self.sendRoutines.toBeExecuted(command, self.socket)

        self.disconnect()
        print(rv)
    
    def __del__(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except AttributeError:
            pass
