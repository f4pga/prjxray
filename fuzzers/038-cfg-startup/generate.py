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
from prjxray import segmaker
from prjxray import verilog
import os
import json
import csv


def bitfilter(frame, word):
    if frame not in [26, 27]:
        return False
    return True

def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")

    with open('params.json', 'r') as f:
        design = json.load(f)

        for d in design['tiles']:
            print("design: " + str(d))
            site = d['site']
            tile = d['tile']

            connection = d['CONNECTION']

            if site.startswith('STARTUP'):
                segmk.add_site_tag(site, 'USRCCLKO_CONNECTED', connection == "CLOCK")

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)

if __name__ == "__main__":
    main()
