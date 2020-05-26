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
"""
This script loads the PS7 pin dump from Vivado and groups pins into ports. Also
assigns each port a class that indicates its function. The classes are:

- "normal": A port that connects to the PL (FPGA)
- "test":   A port used for testing, not accessible from the PL.
- "debug":  A debug port, not accessible.
- "mio":    The "mio" ports go directly to die pads, not relevant for routing.

Ports are then written to a JSON file.
"""
import argparse
import csv
import json
import re

from collections import defaultdict

# =============================================================================


def main():

    BUS_REGEX = re.compile("(.*[A-Z_])([0-9]+)$")

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("csv", type=str, help="PS7 pin dump file")
    parser.add_argument(
        "json",
        type=str,
        help="Output JSON file with PS7 pins grouped into ports")

    args = parser.parse_args()

    # Load pin dump
    with open(args.csv, "r") as fp:
        pin_dump = list(csv.DictReader(fp))

    # Group pins into ports
    ports = defaultdict(lambda :{
        "direction": None,
        "min": None,
        "max": None,
        "width": 0
        })

    for pin in list(pin_dump):

        # Get port name and signal index
        match = BUS_REGEX.match(pin["name"])
        if match:
            name = match.group(1)
            idx = int(match.group(2))
        else:
            name = pin["name"]
            idx = 0

        # Get direction
        is_input = int(pin["is_input"])
        is_output = int(pin["is_output"])
        is_bidir = int(pin["is_bidir"])

        if is_input and not is_output and not is_bidir:
            direction = "input"
        elif not is_input and is_output and not is_bidir:
            direction = "output"
        elif not is_input and not is_output and is_bidir:
            direction = "inout"
        else:
            assert False, pin

        # Add to port
        port = ports[name]

        if port["direction"] is None:
            port["direction"] = direction
        else:
            assert port["direction"] == direction

        if port["min"] is None:
            port["min"] = idx
        else:
            port["min"] = min(port["min"], idx)

        if port["max"] is None:
            port["max"] = idx
        else:
            port["max"] = max(port["max"], idx)

        port["width"] = port["max"] - port["min"] + 1

    # Sort ports by their purpose
    for name, port in ports.items():

        # A test pin (unconnected)
        if name.startswith("TEST"):
            cls = "test"

        # A debug pin (unconnected)
        elif name.startswith("DEBUG"):
            cls = "debug"

        # A MIO/DDR pin.
        elif name.startswith("MIO") or name.startswith("DDR") and \
            name != "DDRARB":
            cls = "mio"

        # PS7 clock/reset
        elif name in ["PSCLK", "PSPORB", "PSSRSTB"]:
            cls = "mio"

        # "Normal" pin
        else:
            cls = "normal"

        port["class"] = cls

    # Write pin ports to a JSON file
    with open(args.json, "w") as fp:
        json.dump(ports, fp, indent=1, sort_keys=True)


# =============================================================================

if __name__ == "__main__":
    main()
