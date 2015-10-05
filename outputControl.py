#!/usr/bin/python3
import os
import select
import time
import sysv_ipc
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)

redLED = False
greenLED = False
yellowLED = False
svSM=sysv_ipc.SharedMemory(0x3000,sysv_ipc.IPC_CREAT,0o666,64)
with os.fdopen(os.open('/tmp/note', os.O_WRONLY | os.O_CREAT, 0o666), 'w') as fl:
    fl.write(str(svSM.id))
svSM.write(b"0000000000000000000000000000000000000000000000000000000000000000")
def redGreenYellow(pin, zeroOne):
    GPIO.output(pin,zeroOne)


def red(zeroOne):
    GPIO.output(11,zeroOne)
    if zeroOne==1:
        svSM.write(b"T",0)
    else:
        svSM.write(b"F",0)

def yellow(zeroOne):
    GPIO.output(13,zeroOne)
    if zeroOne==1:
        svSM.write(b"T",1)
    else:
        svSM.write(b"F",1)

def green(zeroOne):
    GPIO.output(15,zeroOne)
    if zeroOne==1:
        svSM.write(b"T",2)
    else:
        svSM.write(b"F",2)

def turnOffOld():
    GPIO.output(11, 0)
    GPIO.output(13, 0)
    GPIO.output(15, 0)

def turnOff():
    red(0)
    yellow(0)
    green(0)


def switchRed():
    global redLED
    if not redLED:
        redGreenYellow(11, 1)
        redLED = True
    else:
        redGreenYellow(11, 0)
        redLED = False

def switchGreen():
    global greenLED
    if not greenLED:
        redGreenYellow(15, 1)
        greenLED = True
    else:
        redGreenYellow(15, 0)
        greenLED = False

def switchYellow():
    global yellowLED
    if not yellowLED:
        redGreenYellow(13, 1)
        yellowLED = True
    else:
        redGreenYellow(13, 0)
        yellowLED = False

def flash():
    for i in range(5):
        switchRed()
        time.sleep(1)
        switchRed()
        time.sleep(1)
        switchGreen()
        time.sleep(1)
        switchGreen()
        time.sleep(1)
        switchYellow()
        time.sleep(1)
        switchYellow()
        time.sleep(1)

commandPipeFp="/tmp/commandPipe"

commands={
        "switchRed": switchRed,
        "flash": flash,
        "turnOff": turnOff,
        "setRed": lambda: red(1),
        "resetRed": lambda: red(0),
        "setYellow": lambda: yellow(1),
        "resetYellow": lambda: yellow(0),
        "setGreen": lambda: green(1),
        "resetGreen": lambda: green(0),
        }
"""
        "setRed": lambda: redGreenYellow(11, 1),
        "resetRed": lambda: redGreenYellow(11, 0),
        "setYellow": lambda: redGreenYellow(13, 1),
        "resetYellow": lambda: redGreenYellow(13, 0),
        "setGreen": lambda: redGreenYellow(15, 1),
        "resetGreen": lambda: redGreenYellow(15, 0)
"""        

if os.path.exists(commandPipeFp):
    print("pipe already exists!")
    os.unlink(commandPipeFp)
    print("deleting..")


try:
    if os.path.exists(commandPipeFp):
        print("failed to delete old pipe! closing")
        exit(1)
    else:
        os.mkfifo(commandPipeFp, 0o666)
        os.system("sudo chmod 0666 "+commandPipeFp)
        while True:
            inPipe=open(commandPipeFp,"r")
            readReady, writeReady, xList= select.select([inPipe],[],[])
            ind=readReady.index(inPipe)
            if ind>-1:
                rv=readReady[ind].read(4096)
                inPipe.close()
                rv=rv.split()
                for command in rv:
                    if command in commands:
                        commands[command]()
                        print(command)
                    else:
                        print("unrecognized command: "+str(command))
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
    GPIO.cleanup()
    print("cleaned up")

