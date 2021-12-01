import cereal.messaging as messaging
from common.numpy_fast import clip

import time

from can_interface import CANSocket 
from can_interface import send_cmd

sm = messaging.SubMaster(['carControl'])
while 1:
  sm.update()
  throttle_op = clip(sm['carControl'].actuators.accel/1.6, 0.0, 1.0)
  brake_op = clip(-sm['carControl'].actuators.accel/4.0, 0.0, 1.0)
  steer_op = sm['carControl'].actuators.steeringAngleDeg

  send_cmd('0x060', 0, brake_op, 'acc')
  send_cmd('0x062', 0, throttle_op, 'acc')
  steer = (steer_op/360.0*600) + 900
  send_cmd('0xF513', 1, steer, 'steer')
  print("throttle: ", round(throttle_op, 3), "; steer(motor steps): ", round(steer, 3),  "; brake: ", round(brake_op, 3))
  time.sleep(0.02)

# in publisher
#pm = messaging.PubMaster(['sensorEvents'])
#dat = messaging.new_message('sensorEvents', size=1)
#dat.sensorEvents[0] = {"gyro": {"v": [0.1, -0.1, 0.1]}}
#pm.send('sensorEvents', dat)
