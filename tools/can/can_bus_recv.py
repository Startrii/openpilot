import cereal.messaging as messaging
from common.numpy_fast import clip
from cereal import car, log
from selfdrive.controls.lib.longcontrol import LongControl

import time
import math

from can_interface import CANSocket 
from can_interface import listen_cmd
from can_interface import parse_args

#sm = messaging.SubMaster(['carControl'])
pm = messaging.PubMaster(['carControl'])
#pm = messaging.PubMaster(['stMCU'])
args = parse_args()
s = CANSocket(args.interface)
throttle = 0
brake = 0
steer = 0
while 1:
	#sm.update()
	cob_id, data = s.recv()
	throttle = float(listen_cmd(s,'acc'))
	brake = float(listen_cmd(s,'brake'))
	steer = float(listen_cmd(s,'steer'))

#	print("throttle: ", round(throttle, 3), "; steer(motor steps): ", round(steer, 3),	"; brake: ", round(brake, 3))
	#time.sleep(0.02)

# in publisher
	dat = messaging.new_message('carControl')
	#dat.carControl.enabled = True
	dat.carControl.gasDEPRECATED = throttle
	dat.carControl.brakeDEPRECATED = brake;
	dat.carControl.steeringTorqueDEPRECATED = steer;
	#dat.carControl.actuators.gasDEPRECATED = 0;
	#dat.carControl.actuators.brakeDEPRECATED = 0;
	#dat.carControl.actuators.steer = 0.0
	#dat.carControl.actuators.steeringAngleDeg = 0.0
	#dat.carControl.actuators.accel = 0.0
	#dat.carControl.actuators.longControlState = car.CarControl.Actuators.LongControlState.off
	#dat.carControl.active = True
	pm.send('carControl', dat)
	#pm = messaging.PubMaster(['stMCU'])
	#dat = car.STMCU.new_message()
	#dat.throttle = 0.5
	#dat.brake = 0.0
	#dat.steer = 0.0 
	#pm.send('stMCU', dat)
