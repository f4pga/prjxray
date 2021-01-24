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
    """Tool to update the used resources by the fuzzers for each available part.

    Example:
        prjxray$ ./utils/update_resources.py artix7 --db-root database/artix7/
    """
    parser = argparse.ArgumentParser(
        description="Saves all resource information for a family.")

    parser.add_argument(
        'family',
        help="Name of the device family.",
        choices=['artix7', 'kintex7', 'zynq7'])
    util.db_root_arg(parser)

    args = parser.parse_args()
    env = os.environ.copy()
    cwd = os.path.dirname(os.path.abspath(__file__))
    resource_path = os.path.join(
        os.getenv('XRAY_DIR'), 'settings', args.family)
    information = {}

    parts = util.get_parts(args.db_root)
    for part in parts.keys():
        print("Find pins for {}".format(part))
        env['XRAY_PART'] = part
        # Asks with get_package_pins and different filters for pins with
        # specific properties.
        command = "{} -mode batch -source update_resources.tcl".format(
            env['XRAY_VIVADO'])
        result = subprocess.run(
            command.split(' '),
            check=True,
            env=env,
            cwd=cwd,
            stdout=subprocess.PIPE)
        # Formats the output and stores the pins
        output = result.stdout.decode('utf-8').splitlines()
        clk_pins = output[-4].split(' ')
        data_pins = output[-2].strip().split(' ')
        pins = {
            0: clk_pins[0],
            1: data_pins[0],
            2: data_pins[int(len(data_pins) / 2)],
            3: data_pins[-1]
        }
        information[part] = {'pins': pins}

    # Overwrites the <family>/resources.yaml file completly with new data
    util.set_part_resources(resource_path, information)


if __name__ == '__main__':
    main()
