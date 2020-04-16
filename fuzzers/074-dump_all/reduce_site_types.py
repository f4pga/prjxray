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
""" Reduce sites types to prototypes that are always correct.

reduce_tile_types.py generates per tile type site types.  reduce_site_types.py
takes all site types across all tiles and creates generic site types that are
valid for all tile types.

"""

import argparse
import prjxray.lib
import os
import os.path
import re
import json


def main():
    parser = argparse.ArgumentParser(
        description="Reduces per tile site types to generic site types.")
    parser.add_argument('--output_dir', required=True)

    args = parser.parse_args()

    SITE_TYPE = re.compile('^tile_type_(.+)_site_type_(.+)\.json$')
    site_types = {}
    for path in os.listdir(args.output_dir):
        match = SITE_TYPE.fullmatch(path)
        if match is None:
            continue

        site_type = match.group(2)
        if site_type not in site_types:
            site_types[site_type] = []

        site_types[site_type].append(path)

    for site_type in site_types:
        proto_site_type = None
        for instance in site_types[site_type]:
            with open(os.path.join(args.output_dir, instance)) as f:
                instance_site_type = json.load(f)

                for site_pin in instance_site_type['site_pins'].values():
                    if 'index_in_site' in site_pin:
                        del site_pin['index_in_site']

            if proto_site_type is None:
                proto_site_type = instance_site_type
            else:
                prjxray.lib.compare_prototype_site(
                    proto_site_type,
                    instance_site_type,
                )

        with open(os.path.join(args.output_dir,
                               'site_type_{}.json'.format(site_type)),
                  'w') as f:
            json.dump(proto_site_type, f)


if __name__ == '__main__':
    main()
