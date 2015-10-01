#!/usr/bin/python3
import os
import select
import time
import sysv_ipc

commandPipeFp="/tmp/commandPipe"

commands={
        "setRed": lambda: print("setting Red"),
        "resetRed": lambda: print("resetting Red"),
        "setYellow": lambda: print("setting Yellow"),
        "resetYellow": lambda: print("resetting Yellow"),
        "setGreen": lambda: print("setting Green"),
        "resetGreen": lambda: print("resetting Green")
        }


if os.path.exists(commandPipeFp):
    print("pipe already exists!")
    os.unlink(commandPipeFp)
    print("deleting..")
try:
    if os.path.exists(commandPipeFp):
        print("failed to delete old pipe! closing")
        exit(1)
    else:
        os.mkfifo(commandPipeFp, mode=0o660)
        svSM=sysv_ipc.SharedMemory(242424, sysv_ipc.IPC_CREX, mode=0o660, init_character=b"0")
        while True:
            inPipe=open(commandPipeFp,"r")
            readReady, writeReady, xList= select.select([inPipe],[],[])
            ind=readReady.index(inPipe)
            if ind>-1:
                rv=readReady[ind].read(4096)
                rv=rv.split()
                for command in rv:
                    if command in commands:
                        commands[command]()
                    else:
                        print("unrecognized command: "+str(command))
            inPipe.close()
except Exception as e:
    raise e
finally:
    try:
        inPipe.close()
    except NameError:
        pass
    os.unlink(commandPipeFp)
    svSM.remove()
    svSM.detach()
    print("cleaned up")


# In[67]:

svSM=sysv_ipc.SharedMemory(242424, sysv_ipc.IPC_CREX, mode=0o660, init_character=b"0")
svSM.remove()
svSM.detach()

