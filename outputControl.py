#!/usr/bin/python3
import os
import select
import time
import sysv_ipc
import errno
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)    ##PINS as on the BOARD
GPIO.setup(11,GPIO.OUT)     ##RED LED
GPIO.setup(13,GPIO.OUT)     ##YELLOW LED
GPIO.setup(15,GPIO.OUT)     ##GREEN LED
GPIO.setup(7,GPIO.IN)       ##Button

redLED = False
greenLED = False
yellowLED = False
buttonPIN=7
svSM=sysv_ipc.SharedMemory(0x3000,sysv_ipc.IPC_CREAT,0o666,64)
with os.fdopen(os.open('/tmp/note', os.O_WRONLY | os.O_CREAT, 0o666), 'w') as fl:
    fl.write(str(svSM.id))
svSM.write(b"0000000000000000000000000000000000000000000000000000000000000000")
def redGreenYellow(pin, zeroOne):
    GPIO.output(pin,zeroOne)


def red(zeroOne):
    """
    Set or Reset RED LED
    """
    GPIO.output(11,zeroOne)
    if zeroOne==1:
        svSM.write(b"T",0)
    else:
        svSM.write(b"F",0)

def yellow(zeroOne):
    """
    Set or Reset YELLOW LED
    """
    GPIO.output(13,zeroOne)
    if zeroOne==1:
        svSM.write(b"T",1)
    else:
        svSM.write(b"F",1)

def green(zeroOne):
    """
    Set or Reset GREEN LED
    """
    GPIO.output(15,zeroOne)
    if zeroOne==1:
        svSM.write(b"T",2)
    else:
        svSM.write(b"F",2)

def turnOn():
    """
    Turn ALL LEDs ON
    """
    red(1)
    green(1)
    yellow(1)

def turnOff():
    """
    Turn ALL LEDs OFF
    """
    red(0)
    yellow(0)
    green(0)


def switchRed():
    """
    Switch the RED LED
    """
    global redLED
    if not redLED:
        redGreenYellow(11, 1)
        redLED = True
    else:
        redGreenYellow(11, 0)
        redLED = False

def switchGreen():
    """
    Switch the GREEN LED
    """
    global greenLED
    if not greenLED:
        redGreenYellow(15, 1)
        greenLED = True
    else:
        redGreenYellow(15, 0)
        greenLED = False
        #os.close(inPipe)

def switchYellow():
    """
    Switch the YELLOW LED
    """
    global yellowLED
    if not yellowLED:
        redGreenYellow(13, 1)
        yellowLED = True
    else:
        redGreenYellow(13, 0)
        yellowLED = False

def flash():
    """
    Switch the LEDs 5 times
    """
    for i in range(10):
        switchRed()
        switchGreen()
        switchYellow()
        time.sleep(1)

def sequenceGen():
    """
    Trafic lights sequence
    """
    sequence=(
               (1,0,0),
               (1,0,0),
               (1,0,0),
               (1,0,0),
               (1,1,0),
               (1,1,0),
               (0,0,1),
               (0,0,1),
               (0,0,1),
               (0,0,1),
               (0,1,0),
               (0,1,0),
               )
    i=0;
    n=len(sequence)
    while True:
        red(sequence[i][0])
        yellow(sequence[i][1])
        green(sequence[i][2])
        i+=1
        if i >=n:
            i=0
        yield

state=0
timePoint=0

def state0():
    global state, timePoint
    state=1
    red(0)
    yellow(0)
    green(1)
    timePoint=time.time()

def state1():
    global state, timePoint
    if not GPIO.input(buttonPIN):
        state=2
        red(0)
        yellow(1)
        green(0)
        timePoint=time.time()

def state2():
    global state, timePoint
    t=time.time()
    if t-timePoint>=3:
        state=3
        red(1)
        yellow(0)
        green(0)
        timePoint=time.time()

def state3():
    global state, timePoint
    t=time.time()
    if t-timePoint>=6: ##MORE time for RED
        state=4
        red(1)
        yellow(1)
        green(0)
        timePoint=time.time()

def state4():
    global state, timePoint
    t=time.time()
    if t-timePoint>=3:    
        state=5
        red(0)
        yellow(0)
        green(1)
        timePoint=time.time()

def state5():
    global state, timePoint
    t=time.time()
    if t-timePoint>=10:  ##MORE time for GREEN
        state=1
        timePoint=time.time()

def StateMachine():
    """
    Trafic lights sequence
    """
    global state, timePoint
  
    timePoint=time.time()
    conditions=[state0, state1, state2, state3, state4, state5]
    while True:
        conditions[state]()
        yield
activeSequence=None
sequence=StateMachine()


def button():
    """
    TEST the Trafic lights
    """
    

def activateSequence():
    global activeSequence
    activeSequence=1
    svSM.write(b"T",3)
def deactivateSequence():
    global activeSequence
    svSM.write(b"F",3)
    activeSequence=None

commandPipeFp="/tmp/commandPipe"

commands={
        "switchRed": switchRed,
        "switchGreen": switchGreen,
        "switchYellow": switchYellow,
        "flash": flash,
        "turnOff": turnOff,
        "turnOn": turnOn,
        "setRed": lambda: red(1),
        "resetRed": lambda: red(0),
        "setYellow": lambda: yellow(1),
        "resetYellow": lambda: yellow(0),
        "setGreen": lambda: green(1),
        "resetGreen": lambda: green(0),
        "activateSequence": activateSequence,
        "deactivateSequence": deactivateSequence
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
        inPipe=os.open(commandPipeFp,os.O_RDONLY | os.O_NONBLOCK)
        turnOn()
        time.sleep(0.5)
        turnOff()
        time.sleep(0.5)
        turnOn()
        time.sleep(0.5)
        turnOff()
        time.sleep(0.5)
        turnOn()
        time.sleep(0.5)
        turnOff()
        time.sleep(0.5)
        turnOn()
        time.sleep(0.5)
        turnOff()
        while True:
            readReady, writeReady, xList= select.select([inPipe],[],[],0.05)
            if len(readReady):
                ind=readReady.index(inPipe)
                try:
                    rv=os.read(readReady[ind],4096)
                    #os.close(inPipe)
                    rv=rv.decode()
                    rv=rv.split()
                    for command in rv:
                        if command in commands:
                            commands[command]()
                            print(command)
                        else:
                            print("unrecognized command: "+str(command))
                except OSError as err:
                    if err.errno == errno.EAGAIN:
                        pass 
                        
            if activeSequence !=None:
                next(sequence)
            #print("check2\n")
 
except Exception as e:
    raise e
finally:
    try:
        os.close(inPipe)
    except NameError:
        pass
    os.unlink(commandPipeFp)
    svSM.remove()
    svSM.detach()
    GPIO.cleanup()
    print("cleaned up happened")

