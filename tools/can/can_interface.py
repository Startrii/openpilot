import cereal.messaging as messaging
from common.numpy_fast import clip

import argparse
import errno
import logging
import socket
import struct
import sys

from bitstring import BitArray 

class CANSocket(object):

    FORMAT = "<IB3x8s"
    FD_FORMAT = "<IB3x64s"
    CAN_RAW_FD_FRAMES = 5

    def __init__(self, interface=None):
        self.sock = socket.socket(
            socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        if interface is not None:
            self.bind(interface)

    def bind(self, interface):
        self.sock.bind((interface,))
        self.sock.setsockopt(socket.SOL_CAN_RAW, self.CAN_RAW_FD_FRAMES, 1)

    def send(self, cob_id, data, flags=0):
        cob_id = cob_id | flags
        can_pkt = struct.pack(self.FORMAT, cob_id, len(data), data)
        while True:
            self.sock.send(can_pkt)
            #time.sleep(0.02)
            break

    def recv(self, flags=0):
        can_pkt = self.sock.recv(72)

        if len(can_pkt) == 16:
            cob_id, length, data = struct.unpack(self.FORMAT, can_pkt)
        else:
            cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)

        cob_id &= socket.CAN_EFF_MASK
        return (cob_id, data[:length])


def format_data(data):
    return ''.join([hex(byte)[2:] for byte in data])


def generate_bytes(hex_string):
    if len(hex_string) % 2 != 0:
      hex_string = "0" + hex_string

    int_array = []
    for i in range(0, len(hex_string), 2):
        int_array.append(int(hex_string[i:i+2], 16))

    return bytes(int_array)

def send_cmd(can_id, extended, data):
    command = BitArray((int(data * 10)).to_bytes(2, byteorder="little"))
    body = ('0A0000'+command.hex[0]+command.hex[1]+command.hex[2]+command.hex[3]+'000000')
    try:
      s = CANSocket(args.interface)
    except OSError as e:
      sys.stderr.write('Could not send on interface {0}\n'.format('vcan0'))
      sys.exit(e.errno)

    try:
      cob_id = int(can_id, 16)
    except ValueError:
      sys.stderr.write('Invalid cob-id {0}\n'.format(args.cob_id))
      sys.exit(errno.EINVAL)
    s.send(cob_id, generate_bytes(body),socket.CAN_EFF_FLAG if extended else 0)

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('interface', type=str,
                             help='interface name (e.g. vcan0)')

    return parser.parse_args()

args = parse_args()
