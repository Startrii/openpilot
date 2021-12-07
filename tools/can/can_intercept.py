from cereal import log, car
import cereal.messaging as messaging
import time
import struct

sm = messaging.SubMaster(['can', 'sendcan', 'carControl'])

while True:
    sm.update()
    for can in sm['sendcan']:
        print(f"sendcan: addr = {can.address}, data = {can.dat}")
        if can.address == 0x60:
            tmp = struct.unpack('ff', can.dat)
            print(f"sendcan data: accel = {tmp[0]}, deg = {tmp[1]}")
    for can in sm['can']:
        print(f"can: addr = {can.address}, data = {can.dat}")
    cc = sm['carControl']
    print(f"accel = {cc.actuators.accel}, deg = {cc.actuators.steeringAngleDeg}")
    time.sleep(0.01)





