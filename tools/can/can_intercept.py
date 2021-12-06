from cereal import log, car
import cereal.messaging as messaging
import struct

sm = messaging.SubMaster(['sendcan', 'carControl'])

while True:
    sm.update()
    for can in sm['sendcan']:
        if can.address == 0x60:
            tmp = struct.unpack('ff', can.dat)
            print(f"can: accel = {tmp[0]}, deg = {tmp[1]}")
    cc = sm['carControl']
    print(f"accel = {cc.actuators.accel}, deg = {cc.actuators.steeringAngleDeg}")




