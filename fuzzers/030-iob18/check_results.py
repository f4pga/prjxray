#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
""" Sanity checks FASM output from IOB fuzzer.
The IOB fuzzer is fairly complicated, and it's output is hard to verify by
inspection.  For this reason, check_results.py was written to compare the
specimen's generated and their FASM output.  The FASM output does pose a
chicken and egg issue.  The test procedure is a follows:

1. Build the database (e.g. make -j<N> run)
2. Build the database again (e.g. make -j<N> run)
3. Run check_results.py

The second time that the database is run, the FASM files in the specimen's
will have the bits documented by fuzzer.

"""
import argparse
import os
import os.path
from prjxray import verilog
import json
import generate


def process_parts(parts):
    if len(parts) == 0:
        return

    if parts[-1] == 'IN_ONLY':
        yield 'type', ['IBUF', 'IBUFDS']

    if len(parts) > 2 and parts[-2] == 'SLEW':
        yield 'SLEW', verilog.quote(parts[-1])

    if parts[0] == 'PULLTYPE':
        yield 'PULLTYPE', verilog.quote(parts[1])

    if len(parts) > 1 and parts[1] == 'IN':
        yield 'IOSTANDARDS', parts[0].split('_')
        yield 'IN', True

    if len(parts) > 1 and parts[1] == 'IN_DIFF':
        yield 'IOSTANDARDS', parts[0].split('_')
        yield 'IN_DIFF', True

    if len(parts) > 1 and parts[1] == 'DRIVE':
        yield 'IOSTANDARDS', parts[0].split('_')

        if parts[2] == 'I_FIXED':
            yield 'DRIVES', [None]
        else:
            yield 'DRIVES', parts[2].split('_')


def create_sites_from_fasm(fasm_file):
    sites = {}

    diff_tiles = set()

    with open(fasm_file) as f:
        for l in f:
            if 'IOB18' not in l:
                continue

            parts = l.strip().split('.')
            tile = parts[0]
            site = parts[1]

            if 'OUT_DIFF' == site:
                diff_tiles.add(tile)
                continue

            if (tile, site) not in sites:
                sites[(tile, site)] = {
                    'tile': tile,
                    'site_key': site,
                }

            if len(parts) > 3 and 'IN_DIFF' == parts[3]:
                diff_tiles.add(tile)

            for key, value in process_parts(parts[2:]):
                sites[(tile, site)][key] = value

    for key in sites:
        if 'type' not in sites[key]:
            if 'IOSTANDARDS' not in sites[key]:
                sites[key]['type'] = [None]
            else:
                assert 'IOSTANDARDS' in sites[key], sites[key]
                assert 'DRIVES' in sites[key], sites[key]

                if 'IN' in sites[key]:
                    sites[key]['type'] = ['IOBUF', 'IOBUF_DCIEN']
                else:
                    sites[key]['type'] = [
                        "OBUF",
                        "OBUFDS",
                        "OBUFTDS",
                        "OBUFDS_DUAL_BUF",
                        "OBUFTDS_DUAL_BUF",
                    ]

    return sites, diff_tiles


def process_specimen(fasm_file, params_json):
    sites, diff_tiles = create_sites_from_fasm(fasm_file)

    with open(params_json) as f:
        params = json.load(f)

    count = 0
    for p in params['tiles']:
        tile = p['tile']
        for site in p['site'].split(' '):
            site_y = int(site[site.find('Y') + 1:]) % 2

            if generate.skip_broken_tiles(p):
                continue

            site_key = 'IOB_Y{}'.format(site_y)

            if (tile, site_key) not in sites:
                assert p['type'] is None, p
                continue

            site_from_fasm = sites[(tile, site_key)]

            if site_y == 0 or tile not in diff_tiles:
                assert p['type'] in site_from_fasm['type'], (
                    tile, site_key, p['type'], site_from_fasm['type'])
            else:
                # Y1 on DIFF tiles is always none.
                assert p['type'] is None, p

            if p['type'] is None:
                continue

            assert 'PULLTYPE' in p, p
            assert 'PULLTYPE' in site_from_fasm, site_from_fasm

            if verilog.unquote(p['PULLTYPE']) == '':
                # Default is None.
                pulltype = verilog.quote('NONE')
            else:
                pulltype = p['PULLTYPE']

            assert pulltype == site_from_fasm['PULLTYPE'], (
                tile, site_key, p, site_from_fasm)

            assert 'IOSTANDARDS' in site_from_fasm, (tile, site)

            iostandard = verilog.unquote(p['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                iostandard = iostandard[5:]

            assert iostandard in site_from_fasm['IOSTANDARDS'], (
                p['IOSTANDARD'],
                site_from_fasm['IOSTANDARDS'],
            )

            if p['type'] not in ['IBUF', 'IBUFDS']:
                if verilog.unquote(p['SLEW']) == '':
                    # Default is None.
                    slew = verilog.quote('SLOW')
                else:
                    slew = p['SLEW']

                assert slew == site_from_fasm['SLEW'], (
                    tile, site_key, p, site_from_fasm)

                assert 'DRIVES' not in p, p
                assert 'DRIVES' in site_from_fasm, (
                    tile, site, p['type'], site_from_fasm)

                if p['DRIVE'] is None:
                    assert None in site_from_fasm['DRIVES'], (
                        tile, site_key, p['DRIVE'], site_from_fasm['DRIVES'])
                elif p['DRIVE'] == '':
                    if None in site_from_fasm['DRIVES']:
                        # IOSTANDARD has not DRIVE setting, ignore
                        pass
                    else:
                        # Check that drive is at default
                        assert 'I12' in site_from_fasm['DRIVES'], (
                            tile, site_key, p['DRIVE'],
                            site_from_fasm['DRIVES'])
                else:
                    assert 'I{}'.format(
                        p['DRIVE']) in site_from_fasm['DRIVES'], (
                            tile, site_key, p['DRIVE'],
                            site_from_fasm['DRIVES'])

            count += 1

    return count


def scan_specimens():
    for root, dirs, files in os.walk('build'):
        if os.path.basename(root).startswith('specimen_'):
            print('Processing', os.path.basename(root))
            process_specimen(
                fasm_file=os.path.join(root, 'design.fasm'),
                params_json=os.path.join(root, 'params.json'))

    print('No errors found!')


def main():
    parser = argparse.ArgumentParser(description="Verify IOB FASM vs BELs.")

    parser.add_argument('--fasm')
    parser.add_argument('--params')

    args = parser.parse_args()

    if not args.fasm and not args.params:
        scan_specimens()
    else:
        count = process_specimen(fasm_file=args.fasm, params_json=args.params)
        print('No errors found in {} IO sites'.format(count))


if __name__ == "__main__":
    main()
