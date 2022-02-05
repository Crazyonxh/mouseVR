import sock
import hardware

M = hardware.Mouse('mouse0')
G = hardware.GPIO()
S = sock.Sock()

while True:
    # read mouse position and send to PC
    x, y = M.position()
    msg = b'{x},{y}'
    S.send(msg)
    # recv cmd from PC, and see if reward should be given
    cmds = S.recvCmd()
    for cmd in cmds:
        if cmd == '1': G.setReward()
    G.writePins()
    