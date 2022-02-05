import struct
from nonblock import nonblock_read
import time
from gpiozero import LED 
REWARD_DURATION = 0.5

class Mouse:
    def __init__(self,device_name = 'mouse0'):
        self.path = '/dev/input/' + device_name
        self.file = open(self.path,'rb')
        self.x = 0 
        self.y = 0

    def position(self):
        data = nonblock_read(self.file)
        l  = int(len(data) / 3)
        for i in range(l):
            dx,dy = struct.unpack('bb',data[1+i*3:3+i*3])
            self.x += dx
            self.y += dy
        print(self.x, self.y)
        return self.x, self.y

def in_window(tStart,tCur, dur):
    timePassed = tCur - tStart
    if timePassed >= 0 and timePassed <= dur: return True
    else: return False

class GPIO:
    def __init__(self):
        self.actor = LED(21)
        self.t = -100
    
    def setReward(self):
        self.t = time.time()
    
    def writePins(self):
        if in_window(self.t, time.time(), REWARD_DURATION): 
            self.actor.on()
        else:
            self.actor.off()

if __name__ == '__main__':
    M0 = Mouse('mouse0')
    M1 = Mouse('mouse1')
    lt = time.time()

    while True:
        x0,y0 = M0.position()
        x1,y1 = M1.position()
        print('M0: ',(x0,y0), 'M1:', (x1,y1))
        time.sleep(0.1)
        lt = time.time()


        