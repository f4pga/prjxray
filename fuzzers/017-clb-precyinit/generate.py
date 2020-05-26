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

from prjxray.segmaker import Segmaker

segmk = Segmaker("design.bits")

print("Loading tags")
f = open('params.csv', 'r')
f.readline()
for l in f:
    module, loc, loc2 = l.split(',')

    tmp = module.replace('clb_PRECYINIT_0', 'C0')
    tmp = tmp.replace('clb_PRECYINIT_1', 'C1')
    # clb_PRECYINIT_AX => AX
    src = tmp.replace('clb_PRECYINIT_', '')
    '''
    PRECYINIT
                00_12   30_14   30_13
    C1          0       1       0
    AX          1       0       0
    CIN         0       0       1
    C0          0       0       0
    '''
    srcs = ('C0', 'C1', 'AX', 'CIN')
    for asrc in srcs:
        segmk.add_site_tag(loc, "PRECYINIT.%s" % asrc, int(src == asrc))

segmk.compile()
segmk.write()
