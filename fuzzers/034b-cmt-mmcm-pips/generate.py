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

from prjxray.segmaker import Segmaker
import os
import os.path


def bitfilter(frame, word):
    if frame < 25 or frame > 29:
        return False

    return True


def merge_lr_wires(wire):
    wire = wire.replace('CMT_L_LOWER_B', 'CMT_LRMAP_LOWER_B')
    wire = wire.replace('CMT_R_LOWER_B', 'CMT_LRMAP_LOWER_B')
    return wire


def main():
    segmk = Segmaker("design.bits")

    designdata = {}
    tiledata = {}
    pipdata = {}
    ppipdata = {}
    ignpip = set()
    all_clks = {}

    piplists = ['cmt_top_l_lower_b.txt', 'cmt_top_r_lower_b.txt']
    wirelists = ['cmt_top_l_lower_b_wires.txt', 'cmt_top_r_lower_b_wires.txt']
    ppiplists = ['ppips_cmt_top_l_lower_b.db', 'ppips_cmt_top_r_lower_b.db']

    # Load PIP lists
    print("Loading PIP lists...")
    for piplist in piplists:
        with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                               'cmt_top_lower', piplist)) as f:
            for l in f:
                pip, is_directional = l.strip().split(' ')
                tile_type, dst, src = pip.split('.')
                if tile_type not in pipdata:
                    pipdata[tile_type] = []
                    all_clks[tile_type] = set()

                pipdata[tile_type].append((src, dst))
                if dst.split('_')[-1].startswith('CLK'):
                    all_clks[tile_type].add(src)

                if not int(is_directional):
                    pipdata[tile_type].append((dst, src))
                    if src.split('_')[-1].startswith('CLK'):
                        all_clks[tile_type].add(dst)

    wiredata = {}
    for wirelist in wirelists:
        with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                               'cmt_top_lower', wirelist)) as f:
            for l in f:
                tile_type, wire = l.strip().split()

                if tile_type not in wiredata:
                    wiredata[tile_type] = set()

                wiredata[tile_type].add(wire)

    # Load PPIP lists (to exclude them)
    print("Loading PPIP lists...")
    for ppiplist in ppiplists:
        fname = os.path.join(
            os.getenv('FUZDIR'), '..', '071-ppips', 'build', ppiplist)
        with open(fname, 'r') as f:
            for l in f:
                pip_data, pip_type = l.strip().split()

                if pip_type != 'always':
                    continue

                tile_type, dst, src = pip_data.split('.')
                if tile_type not in ppipdata:
                    ppipdata[tile_type] = []

                ppipdata[tile_type].append((src, dst))

    # Load desgin data
    print("Loading design data...")
    with open("design.txt", "r") as f:
        for line in f:
            fields = line.strip().split(",")
            designdata[fields[0]] = fields[1:]

    with open("design_pips.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('CMT_TOP'):
                continue

            if 'UPPER_B' in tile:
                continue
            if 'LOWER_T' in tile:
                continue

            pip_prefix, _ = pip.split(".")
            tile_from_pip, tile_type = pip_prefix.split('/')
            assert tile == tile_from_pip
            _, src = src.split("/")
            _, dst = dst.split("/")
            pnum = int(pnum)
            pdir = int(pdir)

            if tile not in tiledata:
                tiledata[tile] = {
                    "type": tile_type,
                    "pips": set(),
                    "srcs": set(),
                    "dsts": set(),
                }

            tiledata[tile]["pips"].add((src, dst))
            tiledata[tile]["srcs"].add(src)
            tiledata[tile]["dsts"].add(dst)

            if pdir == 0:
                tiledata[tile]["srcs"].add(dst)
                tiledata[tile]["dsts"].add(src)

            #if dst.startswith('CMT_TOP_R_LOWER_B_CLK') or \
            #   dst.startswith('CMT_TOP_L_LOWER_B_CLK'):
            #    ignpip.add((src, dst))

    active_wires = {}
    with open("design_wires.txt", "r") as f:
        for l in f:
            tile, wire = l.strip().split('/')

            if tile not in active_wires:
                active_wires[tile] = set()

            active_wires[tile].add(wire)

    tags = {}

    # Populate IN_USE tags
    for tile, (site, in_use) in designdata.items():
        if tile not in tags:
            tags[tile] = {}

        tile_type = tile.rsplit("_", maxsplit=1)[0]
        tags[tile]["IN_USE"] = int(in_use)

    # Populate PIPs
    active_clks = {}
    for tile in tags.keys():
        tile_type = tile.rsplit("_", maxsplit=1)[0]

        in_use = tags[tile]["IN_USE"]

        if not in_use:
            active_pips = []
        else:
            active_pips = tiledata[tile]["pips"]

        for src, dst in pipdata[tile_type]:

            if (src, dst) in ignpip:
                continue
            if (src, dst) in ppipdata[tile_type]:
                continue

            tag = "{}.{}".format(merge_lr_wires(dst), merge_lr_wires(src))
            val = in_use if (src, dst) in active_pips else False

            if not (in_use and not val):
                if tile not in active_clks:
                    active_clks[tile] = set()

                active_clks[tile].add(src)
                tags[tile][tag] = int(val)

        for wire in wiredata[tile_type]:
            if 'CLK' not in wire:
                continue

            if 'CLKOUT' in wire:
                continue

            if 'CLKFB' in wire:
                continue

            if 'REBUF' in wire:
                continue

            wire = merge_lr_wires(wire)

            if tile not in active_wires:
                active_wires[tile] = set()
            segmk.add_tile_tag(
                tile, '{}_ACTIVE'.format(wire), wire in active_wires[tile])

    # Output tags
    for tile, tile_tags in tags.items():
        for t, v in tile_tags.items():
            segmk.add_tile_tag(tile, t, v)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
