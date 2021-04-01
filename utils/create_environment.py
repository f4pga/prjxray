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

import os

from prjxray.util import get_part_information, get_part_resources, get_fabric_for_part


def get_environment_variables():
    """
    This function returns a dict of environment settings for a given part.

    It requires a basic setup of the prjxray environment that contains
    information about the databse directory location, the FPGA part, etc.

    One of the settings must be sourced, to set up the basic environment.
    """
    environment = dict()

    # Get base environment variables and resources' paths
    part = os.environ['XRAY_PART']
    database = os.environ['XRAY_DATABASE']
    database_dir = os.environ['XRAY_DATABASE_DIR']
    xray_root = os.environ['XRAY_DIR']
    db_root = os.path.join(database_dir, database)
    res_path = os.path.join(xray_root, 'settings', database)

    # Get device information
    part_info = get_part_information(db_root, part)
    fabric = get_fabric_for_part(db_root, part)
    resources = get_part_resources(res_path, os.environ['XRAY_PART'])

    environment['XRAY_DEVICE'] = part_info['device']
    environment['XRAY_PACKAGE'] = part_info['package']
    environment['XRAY_SPEED_GRADE'] = part_info['speedgrade']
    environment['XRAY_FABRIC'] = fabric
    for number, pin in resources['pins'].items():
        environment['XRAY_PIN_{:02d}'.format(number)] = pin

    return environment


def main():
    # Only dump the environment when the resource.yaml file for the family
    # exists to prevent errors during the creation on the stdout.
    # SKIP_ENV in the environment turns off the environment dump for updating
    # all parts and resources, which will create the resource.yaml file.
    if 'SKIP_ENV' in os.environ:
        return

    environment = get_environment_variables()

    for key, value in environment.items():
        print("export {}={}".format(key, value))


if __name__ == "__main__":
    main()
