import socket
import time
PORT = 11001
HOST = '192.168.43.44'

class Sock:
    def __init__(self):
        listener = socket.socket()
        # HOST = socket.gethostname() # 获取本地主机名
        listener.bind((HOST, PORT))        # 绑定端口
        print('listenning on ', (HOST, PORT))
        listener.listen(600)
        self.sock, addr = listener.accept()
        # self.sock.settimeout(0)
        self.buffer = ''
        print('Connected to ', addr)
        listener.close()

    def send(self,msg):
        msg = msg + '\n'
        data = msg.encode('utf-8')
        self.sock.send(data)
    
    def recv(self):
        data = self.sock.recv(1024)
        msg = data.decode()
        return msg
    
    def recvCmd(self):
        data = self.recv()
        if not data: return 
        data = self.buffer + data
        cmds = data.split('\n')
        try:
            self.buffer = cmds[-1] # 最后分割的一定是不完整的，暂时储存到buffer里
        except:
            self.buffer = ''
        cmds = cmds[:-1]
        return cmds

if __name__ == '__main__':
    S = Sock()
    while True:
        cmds = S.recvCmd()
        if not cmds: continue
        print(cmds)
        for cmd in cmds:
            S.send(cmd)
    # S.send(msg)
