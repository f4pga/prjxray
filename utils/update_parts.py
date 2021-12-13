#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2021  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import argparse
import yaml
import subprocess
import os
import re
from prjxray import util


def main():
    """Tool to update all supported, available parts in a mapping file for the
    given family. It will read all parts from Vivado, filter them by the family,
    and will only add these where a device exists for.

    Example:
        prjxray$ ./utils/update_parts.py artix7 --db-root database/artix7/
    """
    parser = argparse.ArgumentParser(
        description="Saves all supported parts for a family.")

    parser.add_argument(
        'family',
        help="Name of the device family.",
        choices=['artix7', 'kintex7', 'zynq7', 'spartan7'])
    util.db_root_arg(parser)

    args = parser.parse_args()
    env = os.environ.copy()
    # Vivado does not use the suffix 7 for zynq
    env['FILTER'] = "zynq" if args.family == "zynq7" else args.family
    cwd = os.path.dirname(os.path.abspath(__file__))
    information = {}

    # Read all supported devices
    supported_devices = util.get_devices(args.db_root).keys()

    # Fetch all parts for a family (FILTER = family)
    command = "{} -mode batch -source update_parts.tcl".format(
        env['XRAY_VIVADO'])
    result = subprocess.run(
        command.split(' '),
        check=True,
        env=env,
        cwd=cwd,
        stdout=subprocess.PIPE)
    parts = result.stdout.decode('utf-8').split('# }\n')[1].splitlines()[:-1]

    # Splits up the part number and checks if the device is supported
    for part in parts:
        part, device, package, speed = part.split(',')
        if device in supported_devices:
            information[part] = {
                'device': device,
                'package': package,
                'speedgrade': speed[1:]
            }
        else:
            print("Part {} has an unsupported device {}".format(part, device))

    # Overwrites the <family>/parts.yaml file completly with new data
    util.set_part_information(args.db_root, information)


if __name__ == '__main__':
    main()
