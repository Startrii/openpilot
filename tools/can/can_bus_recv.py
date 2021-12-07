import cereal.messaging as messaging
from common.numpy_fast import clip
from cereal import car, log
from selfdrive.controls.lib.longcontrol import LongControl

import time
import math

from can_interface import CANSocket 
from can_interface import listen_cmd
from can_interface import parse_args

pm = messaging.PubMaster(['stMCU'])
args = parse_args()
s = CANSocket(args.interface)
throttle = 0
brake = 0
steer = 900
while 1:
	dat = messaging.new_message('stMCU')
	dat.stMCU.throttle = throttle
	dat.stMCU.brake = brake
	dat.stMCU.steer = steer
	pm.send('stMCU', dat)

	#sm.update()
	cob_id, data = s.recv()
	#throttle = float(listen_cmd(s,'acc'))
	#brake = float(listen_cmd(s,'brake'))
	steer = float(listen_cmd(s,'steer'))

	print("throttle: ", round(throttle, 3), "; steer(motor steps): ", round(steer, 3),	"; brake: ", round(brake, 3))
	time.sleep(0.02)

# in publisher
	dat = messaging.new_message('stMCU')
	dat.stMCU.throttle = throttle
	dat.stMCU.brake = brake
	dat.stMCU.steer = steer 
	pm.send('stMCU', dat)
