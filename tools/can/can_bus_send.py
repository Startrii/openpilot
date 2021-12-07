import cereal.messaging as messaging
from common.numpy_fast import clip
from cereal import car, log

import time

from can_interface import CANSocket 
from can_interface import send_cmd

sm = messaging.SubMaster(['carControl', 'stMCU'])
throttle_op = 0
brake_op = 0
steer_op = 0
old_steer = 0
steer_out = 0
STEER_RATIO = 22.15
max_steer_angle = 35.0
is_openpilot_engaged = False

def steer_rate_limit(old, new):
  # Rate limiting to 0.5 degrees per step
  limit = 0.5
  if new > old + limit:
    return old + limit
  elif new < old - limit:
    return old - limit
  else:
    return new

while 1:
	sm.update(0)
	print(sm['stMCU'])
	is_openpilot_engaged = sm['carControl'].enabled
	if is_openpilot_engaged :	
		throttle_op = clip(sm['carControl'].actuators.accel/1.6, 0.0, 1.0)
		brake_op = clip(-sm['carControl'].actuators.accel/4.0, 0.0, 1.0)
		steer_op = sm['carControl'].actuators.steeringAngleDeg

		steer_out = steer_op

		steer_out = steer_rate_limit(old_steer, steer_out)
		old_steer = steer_out

	#steer_carla = steer_out / (max_steer_angle * STEER_RATIO * -1)
	
	send_cmd('0x060', 0, brake_op, 'acc')
	send_cmd('0x062', 0, throttle_op/1.6, 'acc')
	steer = (steer_out/360.0*600) + 900
	send_cmd('0xF513', 1, steer, 'steer')
	print("throttle: ", round(throttle_op, 3), "; steer(motor steps): ", round(steer, 3), steer_op, "; brake: ", round(brake_op, 3))
	time.sleep(0.02)

