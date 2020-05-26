#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
'''
Extract the frames from the output of the prjxray bitread tool.
'''

import sys
import re


def extract_frames(args):
    """ Extract the frame addresses and the corresponding content """
    frames_dict = dict()
    with open(args[1], 'r') as f:
        parse_frames = False
        for cnt, line in enumerate(f):
            if line.startswith("\n"):
                parse_frames = False
                continue
            line = line.strip()
            if not parse_frames and not line.startswith("Frame"):
                continue
            if line.startswith("Frame"):
                match = re.match("Frame 0x([0-9a-fA-F]+) ", line)
                frame_addr = "0x" + match.group(1).upper()
                parse_frames = True
                frames_dict[frame_addr] = list()
                continue
            for frame in line.split():
                frames_dict[frame_addr].append("0x" + frame.upper())
    for addr, words in frames_dict.items():
        print("{addr} {words}".format(addr=addr, words=",".join(words)))


if __name__ == "__main__":
    extract_frames(sys.argv)
