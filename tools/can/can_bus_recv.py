import cereal.messaging as messaging
from common.numpy_fast import clip
from cereal import car, log
from selfdrive.controls.lib.longcontrol import LongControl

import time
import math

from can_interface import CANSocket 
from can_interface import listen_cmd
from can_interface import parse_args
from bitstring import BitArray

#pm = messaging.PubMaster(['stMCU'])
args = parse_args()
s = CANSocket(args.interface, '063:7FF')
throttle = 0
brake = 0
steer = 900


while 1:
	#dat = messaging.new_message('stMCU')
	#dat.stMCU.throttle = throttle
	#dat.stMCU.brake = brake
	#dat.stMCU.steer = steer
	#pm.send('stMCU', dat)

	#sm.update()
	#cob_id, data = s.recv()
	#throttle = float(listen_cmd(s,'acc'))
	#brake = float(listen_cmd(s,'brake'))
	#steer = float(listen_cmd(s,'steer'))
	if (s.recv()):
		cob_id, data = s.recv()
		if (cob_id == 0x063):
			command = (BitArray(uint=data[5], length=8) + BitArray(uint=data[4], length=8))
			throttle = command.uint/65535.0
		if (cob_id == 0x061):
			command = (BitArray(uint=data[5], length=8) + BitArray(uint=data[4], length=8))
			brake = command.uint/65535.0
		if (cob_id == 0x13F5):
			angel = (BitArray(uint=data[4], length=8)+BitArray(uint=data[3], length=8))
			steer = angel.uint/10.0

	print("id", cob_id, "throttle: ", round(throttle, 3), "; steer(motor steps): ", round(steer, 3),	"; brake: ", round(brake, 3))
	#time.sleep(0.02)

# in publisher
	#dat = messaging.new_message('stMCU')
	#dat.stMCU.throttle = throttle
	#dat.stMCU.brake = brake
	#dat.stMCU.steer = steer 
	#pm.send('stMCU', dat)
