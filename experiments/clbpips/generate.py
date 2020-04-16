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

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        line, active = line.split()
        tile, pip = line.split("/")
        _, pip = pip.split(".")

        print(tile, pip, active)
        segmk.addtag(tile, pip, int(active))

segmk.compile()
segmk.write()
