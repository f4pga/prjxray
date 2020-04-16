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
'''
module,loc,bel,n
clb_NCY0_MX,SLICE_X12Y100,A6LUT,3
clb_NCY0_O5,SLICE_X16Y100,C6LUT,0
clb_NCY0_O5,SLICE_X17Y100,A6LUT,2
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    module, loc, bel, n = l.split(',')
    n = int(n)
    # A, B, etc
    which = bel[0]

    # One bit, set on O5
    segmk.add_site_tag(loc, "CARRY4.%cCY0" % which, module == 'clb_NCY0_O5')
segmk.compile()
segmk.write()
