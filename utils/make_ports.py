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
This script loads the pin dump of the desired BEL from Vivado and groups pins into ports.

Ports that are not connected to the PL are not included. These ports are usually test and
debug related ports, which are not useful from a P&R perspective.

Ports are then written to a JSON file.
"""
import argparse
import csv
import json
import re

from collections import defaultdict

from prjxray.util import OpenSafeFile


def main():

    BUS_REGEX = re.compile("(.*[A-Z_])([0-9]+)$")

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("csv", type=str, help="BEL pin dump file")
    parser.add_argument(
        "json",
        type=str,
        help="Output JSON file with BEL pins grouped into ports")

    parser.add_argument(
        "--special-pins",
        default="",
        type=str,
        required=False,
        help="Some pins cannot be decoded with the regex")

    args = parser.parse_args()

    # Load pin dump
    with OpenSafeFile(args.csv, "r") as fp:
        pin_dump = list(csv.DictReader(fp))

    # Group pins into ports
    ports = defaultdict(lambda: {"direction": None, "width": 0})

    special_pins = args.special_pins.split(",")

    for pin in list(pin_dump):
        pin_name = pin["name"]

        name = None
        if pin_name in special_pins:
            # Full match
            name = pin_name
        else:
            # Partial match
            for special_pin in special_pins:
                if pin_name.startswith(special_pin):
                    name = special_pin
                    break

        if name is None:
            match = BUS_REGEX.match(pin_name)
            if match:
                name = match.group(1)
            else:
                name = pin_name

        # Get direction
        is_input = int(pin["is_input"])
        is_output = int(pin["is_output"])
        is_clock = int(pin["is_clock"])

        if is_input:
            direction = "input"
            if is_clock:
                direction = "clock"
        elif is_output:
            direction = "output"
        else:
            assert False, pin

        # Add to port
        port = ports[name]

        if port["direction"] is None:
            port["direction"] = direction
        else:
            assert port["direction"] == direction, (port, direction, name)

        port["width"] += 1

    # Write pin ports to a JSON file
    with OpenSafeFile(args.json, "w") as fp:
        json.dump(ports, fp, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
