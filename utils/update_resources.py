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
import tempfile
import json
from prjxray.util import OpenSafeFile, db_root_arg, get_parts, set_part_resources


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
        choices=['artix7', 'kintex7', 'zynq7', 'spartan7'])
    db_root_arg(parser)

    args = parser.parse_args()
    env = os.environ.copy()
    cwd = os.path.dirname(os.path.abspath(__file__))
    resource_path = os.path.join(
        os.getenv('XRAY_DIR'), 'settings', args.family)
    information = {}

    parts = get_parts(args.db_root)
    processed_parts = dict()
    for part in parts.keys():
        # Skip parts which differ only in the speedgrade, as they have the same pins
        fields = part.split("-")
        common_part = fields[0]
        if common_part in processed_parts:
            information[part] = processed_parts[common_part]
            continue

        print("Find pins for {}".format(part))
        env['XRAY_PART'] = part
        _, tmp_file = tempfile.mkstemp()
        # Asks with get_package_pins and different filters for pins with
        # specific properties.
        command = "env TMP_FILE={} {} -mode batch -source update_resources.tcl".format(
            tmp_file, env['XRAY_VIVADO'])
        result = subprocess.run(
            command.split(' '),
            check=True,
            env=env,
            cwd=cwd,
            stdout=subprocess.PIPE)

        with OpenSafeFile(tmp_file, "r") as fp:
            pins_json = json.load(fp)

        os.remove(tmp_file)

        clk_pins = pins_json["clk_pins"].split()
        data_pins = pins_json["data_pins"].split()
        pins = {
            0: clk_pins[0],
            1: data_pins[0],
            2: data_pins[int(len(data_pins) / 2)],
            3: data_pins[-1]
        }
        information[part] = {'pins': pins}
        processed_parts[common_part] = {'pins': pins}

    # Overwrites the <family>/resources.yaml file completly with new data
    set_part_resources(resource_path, information)


if __name__ == '__main__':
    main()
