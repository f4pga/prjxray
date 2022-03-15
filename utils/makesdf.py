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

import json
import argparse

from prjxray.util import OpenSafeFile

def get_elems_count(timings, slice, site, bel_type):
    combinational = 0
    sequential = 0
    for delay in timings[slice][site][bel_type]:
        if 'sequential' in timings[slice][site][bel_type][delay]:
            sequential += 1
        else:
            combinational += 1
    return combinational, sequential


def produce_sdf(timings, outdir):

    for slice in timings:
        sdf = \
"""
(DELAYFILE
    (SDFVERSION \"3.0\")
    (TIMESCALE 1ns)
"""
        for site in sorted(timings[slice]):
            for bel_type in sorted(timings[slice][site]):
                combinational, sequential = get_elems_count(
                    timings, slice, site, bel_type)
                #define CELL
                cell= \
"""
    (CELL
        (CELLTYPE \"{name}\")
        (INSTANCE {location})""".format(name=bel_type.upper(), location=site)
                sdf += cell

                #define delay header (if needed)
                if combinational > 0:
                    delay_hdr = \
"""
        (DELAY
            (ABSOLUTE"""
                    sdf += delay_hdr
                    # add all delays definitions
                    for delay in sorted(timings[slice][site][bel_type]):
                        if 'sequential' in timings[slice][site][bel_type][
                                delay]:
                            continue
                        dly = \
"""
                (IOPATH {input} {output} ({FAST_MIN}::{FAST_MAX})({SLOW_MIN}::{SLOW_MAX}))""".format(**timings[slice][site][bel_type][delay])
                        if 'extra_ports' in timings[slice][site][bel_type][
                                delay] is not None:
                            dly += \
""" #extra ports {}""".format(timings[slice][site][bel_type][delay]['extra_ports'])

                        sdf += dly

                    # close DELAY definition
                    enddelay = \
"""
            )
        )"""
                    sdf += enddelay

                # define TIMINGCHECK header (if needed)
                if sequential > 0:
                    timingcheck_hdr = \
"""
        (TIMINGCHECK"""
                    sdf += timingcheck_hdr

                    for delay in sorted(timings[slice][site][bel_type]):
                        if 'sequential' not in timings[slice][site][bel_type][
                                delay]:
                            continue
                        timingcheck = \
"""
            ({prop} {input} (posedge {clock}) ({SLOW_MIN}::{SLOW_MAX}))""".format(
                        prop=timings[slice][site][bel_type][delay]['sequential'].upper(),
                        **timings[slice][site][bel_type][delay])

                        if 'extra_ports' in timings[slice][site][bel_type][
                                delay] is not None:
                            timingcheck += \
""" #extra ports {}""".format(timings[slice][site][bel_type][delay]['extra_ports'])

                        sdf += timingcheck

                    # close TIMINGCHECK definition
                    endtimingcheck = \
"""
        )"""
                    sdf += endtimingcheck

                endcell = \
"""
    )"""
                sdf += endcell
        # end of SDF
        sdf += \
"""
)"""

        with OpenSafeFile(outdir + '/' + slice + '.sdf', "w") as fp:
            fp.write(sdf)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--json', type=str, help="Input JSON file")
    parser.add_argument('--sdf', type=str, help="SDF files output directory")

    args = parser.parse_args()

    with OpenSafeFile(args.json, 'r') as fp:
        timings = json.load(fp)

    produce_sdf(timings, args.sdf)


if __name__ == '__main__':
    main()
