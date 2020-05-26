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

from prjxray import bitstream


def write(bits_fn, fnout, tags):
    '''
    seg 00020000_046
    bit 18_20
    bit 39_63
    tag LIOB33.IOB_Y1.REFBIT 0
    '''
    fout = open(fnout, "w")

    def line(s):
        fout.write(s + "\n")

    # Everything relative to start of bitstream
    line("seg 00000000_000")

    bitdata = bitstream.load_bitdata2(open(bits_fn, "r"))

    for frame, words in bitdata.items():
        for word, wbits in words.items():
            for bitidx in sorted(list(wbits)):
                # Are the names arbitrary? Lets just re-create
                line("bit %08X_%03u_%02u" % (frame, word, bitidx))

    for k, v in tags.items():
        line("tag %s %u" % (k, v))
