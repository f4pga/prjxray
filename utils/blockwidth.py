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
Prints minor address group sizes
If any part of an IP block is written, Vivado likes to write the entire block
This can be useful to guess the number of frames an IP block uses

This was developed with PERFRAMECRC, but could probably be rewritten to work without it
'''

import sys
import os
import time
import json
import subprocess
from io import StringIO

BITTOOL = os.getenv('XRAY_BITTOOL')


def bit2packets(fn):
    # capture_output wasn't added until 3.7, I have 3.5
    #return subprocess.run([BITTOOL, "list_config_packets", fn], capture_output=True, check=True).stdout
    p = subprocess.run(
        [BITTOOL, "list_config_packets", fn],
        check=True,
        stdout=subprocess.PIPE)
    return p.stdout.decode("ascii")


def nominor(addr):
    return addr & ~0x7f


def gen_frame_writes(f):
    '''
    look for line triples like this

    [Write Type=1 Address= 1 Length=         1 Reg="Frame Address"]
    Data in hex:
          1d

    '''
    while True:
        l = f.readline()
        if not l:
            break
        l = l.strip()
        # TODO: assert that writes are always per frame CRC
        if l != '[Write Type=1 Address= 1 Length=         1 Reg="Frame Address"]':
            continue
        assert f.readline().strip() == 'Data in hex:'
        lhex = f.readline().strip()
        yield int(lhex, 16)


def gen_major_writes(fnin):
    '''
    The same address can appear twice
    Ex: 0x00800000
    Moved from counter to set
    '''
    last_addrs = None
    last_major = None

    for this_minor in gen_frame_writes(StringIO(bit2packets(fnin))):
        this_major = nominor(this_minor)

        if this_major == last_major:
            # should be no gaps
            last_addrs.add(this_minor)

            # addresses may skip back, but they don't seem to skip forward
            # AssertionError: (0, 2, {0, 1})
            # assert (this_major - this_minor) + 1 == len(last_addrs), (this_major, len(last_addrs), last_addrs)
            assert (this_major - this_minor) + 1 <= len(last_addrs), (
                this_major, len(last_addrs), last_addrs)
        else:
            if last_major is not None:
                assert len(last_addrs) <= 0x80
                yield last_major, len(last_addrs)

            # all writes should start at base?
            assert this_major == this_minor
            last_major = this_major
            last_addrs = set([this_minor])
    yield last_major, len(last_addrs)


def run(fnin, verbose=False):
    for addr, nframes in gen_major_writes(fnin):
        print('0x%08X: 0x%02X' % (addr, nframes))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Print PERFRAMECRC bitstream minor address gropuing')
    parser.add_argument('fnin', default=None, help='input bitstream')
    args = parser.parse_args()

    run(args.fnin, verbose=False)


if __name__ == '__main__':
    main()
