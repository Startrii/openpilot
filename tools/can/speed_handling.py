import cereal.messaging as messaging
from common.numpy_fast import clip
from opendbc.can.packer import CANPacker
from opendbc.can.parser import CANParser
from selfdrive.boardd.boardd_api_impl import can_list_to_can_capnp  # pylint: disable=no-name-in-module,import-error
from selfdrive.car import crc8_pedal

import argparse
import errno
import logging
import socket
import struct
import sys
import time
import os
import signal
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from bitstring import BitArray


class CANSocket(object):

    FORMAT = "<IB3x8s"
    FD_FORMAT = "<IB3x64s"
    CAN_RAW_FD_FRAMES = 5

    def __init__(self, interface=None):
        self.sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW,
                                  socket.CAN_RAW)
        if interface is not None:
            self.bind(interface)

    def bind(self, interface):
        self.sock.bind((interface, ))
        self.sock.setsockopt(socket.SOL_CAN_RAW, self.CAN_RAW_FD_FRAMES, 1)

    def send(self, cob_id, data, flags=0):
        cob_id = cob_id | flags
        can_pkt = struct.pack(self.FORMAT, cob_id, len(data), data)
        self.sock.send(can_pkt)
        # time.sleep(0.02)

    def recv(self, flags=0):
        can_pkt = self.sock.recv(72)

        if len(can_pkt) == 16:
            cob_id, length, data = struct.unpack(self.FORMAT, can_pkt)
        else:
            cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)

        cob_id &= socket.CAN_EFF_MASK
        return (cob_id, data[:length])


def can_function(pm, speed, angle, idx, cruise_button, is_engaged):
    packer = CANPacker("honda_civic_touring_2016_can_generated")
    rpacker = CANPacker("acura_ilx_2016_nidec")
    msg = []

    # *** powertrain bus ***

    speed = speed * 3.6  # convert m/s to kph
    msg.append(
        packer.make_can_msg("ENGINE_DATA", 0, {"XMISSION_SPEED": speed}, idx))
    msg.append(
        packer.make_can_msg(
            "WHEEL_SPEEDS", 0, {
                "WHEEL_SPEED_FL": speed,
                "WHEEL_SPEED_FR": speed,
                "WHEEL_SPEED_RL": speed,
                "WHEEL_SPEED_RR": speed
            }, -1))

    msg.append(packer.make_can_msg("SCM_BUTTONS", 0, {"CRUISE_BUTTONS": cruise_button}, idx))

    values = {"COUNTER_PEDAL": idx & 0xF}
    checksum = crc8_pedal(packer.make_can_msg("GAS_SENSOR", 0, {"COUNTER_PEDAL": idx & 0xF}, -1)[2][:-1])
    values["CHECKSUM_PEDAL"] = checksum
    msg.append(packer.make_can_msg("GAS_SENSOR", 0, values, -1))

    msg.append(packer.make_can_msg("GEARBOX", 0, { "GEAR": 4, "GEAR_SHIFTER": 8}, idx))
    msg.append(packer.make_can_msg("GAS_PEDAL_2", 0, {}, idx))
    msg.append(packer.make_can_msg("SEATBELT_STATUS", 0, {"SEATBELT_DRIVER_LATCHED": 1}, idx))
    msg.append(packer.make_can_msg("STEER_STATUS", 0, {}, idx))
    msg.append(packer.make_can_msg("STEERING_SENSORS", 0, {"STEER_ANGLE": angle}, idx))
    msg.append(packer.make_can_msg("VSA_STATUS", 0, {}, idx))
    msg.append(packer.make_can_msg("STANDSTILL", 0, {"WHEELS_MOVING": 1 if speed >= 1.0 else 0}, idx))
    msg.append(packer.make_can_msg("STEER_MOTOR_TORQUE", 0, {}, idx))
    msg.append(packer.make_can_msg("HUD_SETTING", 0, {}, idx))
    msg.append(packer.make_can_msg("EPB_STATUS", 0, {}, idx))
    msg.append(packer.make_can_msg("DOORS_STATUS", 0, {}, idx))
    msg.append(packer.make_can_msg("CRUISE_PARAMS", 0, {}, idx))
    msg.append(packer.make_can_msg("CRUISE", 0, {}, idx))
    msg.append(packer.make_can_msg("SCM_FEEDBACK", 0, {"MAIN_ON": 1}, idx))
    msg.append(packer.make_can_msg("POWERTRAIN_DATA", 0, {"ACC_STATUS": int(is_engaged)}, idx))

    # *** cam bus ***
    msg.append(packer.make_can_msg("STEERING_CONTROL", 2, {}, idx))
    msg.append(packer.make_can_msg("ACC_HUD", 2, {}, idx))
    msg.append(packer.make_can_msg("BRAKE_COMMAND", 2, {}, idx))

    # *** radar bus ***
    if idx % 5 == 0:
        msg.append( rpacker.make_can_msg("RADAR_DIAGNOSTIC", 1, {"RADAR_STATE": 0x79}, -1))
        for i in range(16):
            msg.append( rpacker.make_can_msg("TRACK_%d" % i, 1, {"LONG_DIST": 255.5}, -1))

    pm.send('can', can_list_to_can_capnp(msg))

def main():
    interface = 'vcan0'
    pm = messaging.PubMaster(['can'])
    i = 0

    try:
        s = CANSocket(interface)
    except OSError as e:
        sys.stderr.write('Could not send on interface {0}\n'.format('vcan0'))
        sys.exit(e.errno)

    while True:
        can_id, data = s.recv()
        print(data)
        if can_id == 0x60:
            speed, angle, cruise_button, is_engaged = struct.unpack('eeB?', data)
        print(speed, angle, cruise_button, is_engaged)
        can_function(pm, speed, angle, i, cruise_button, is_engaged)
        # can_function(pm, vs.speed, vs.angle, i, vs.cruise_button, vs.is_engaged)
        time.sleep(0.01)
        i += 1

if __name__ == '__main__':
    main()
