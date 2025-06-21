#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import argparse
import os
from prjxray import util


def main():
    """Script for creating symlinks to device files within the db directory
    in case a device has an identical fabric.

    """
    parser = argparse.ArgumentParser(
        description="Creates symlinks for devices with identical fabric.")

    util.db_root_arg(parser)
    args = parser.parse_args()

    # Create links for all devices listed in the devices.yaml mapping file
    devices = util.get_devices(args.db_root)
    for device in devices:
        dst = os.path.join(args.db_root, device)
        if os.path.exists(dst):
            continue
        fabric = devices[device]['fabric']
        src = os.path.join(args.db_root, fabric)
        assert os.path.exists(src), "Fabric db files don't exist"
        os.symlink(src, dst)


if __name__ == '__main__':
    main()
