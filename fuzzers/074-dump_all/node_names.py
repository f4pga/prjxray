#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
""" This script creates node_wires.json, which describes how nodes are named.

This script consumes the raw node data from root_dir and outputs
node_wires.json to the output_dir.

The class prjxray.node_model.NodeModel can be used to reconstruct node names
and node <-> wire mapping.

The contents of node_wires.json is:
 - The set of tile type wires that are always nodes, key "node_pattern_wires"
 - The set of tile wires that are nodes within the graph, key
   "specific_node_wires".

"""

import argparse
import datetime
import json
import multiprocessing
import progressbar
import pyjson5 as json5
import os.path

from prjxray import util, lib
from prjxray.grid import Grid


def read_json5(fname):
    with open(fname, 'r') as f:
        return json5.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Reduce node names for wire connections.")
    parser.add_argument('--root_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--max_cpu', type=int, default=10)

    args = parser.parse_args()

    _, nodes = lib.read_root_csv(args.root_dir)

    processes = min(multiprocessing.cpu_count(), args.max_cpu)
    pool = multiprocessing.Pool(processes=processes)

    # Read tile grid and raw node data.
    print('{} Reading tilegrid'.format(datetime.datetime.now()))
    with open(os.path.join(util.get_db_root(), util.get_fabric(),
                           'tilegrid.json')) as f:
        grid = Grid(db=None, tilegrid=json.load(f))

    raw_node_data = []
    with progressbar.ProgressBar(max_value=len(nodes)) as bar:
        for idx, node in enumerate(pool.imap_unordered(
                read_json5,
                nodes,
                chunksize=20,
        )):
            bar.update(idx)
            raw_node_data.append(node)
            bar.update(idx + 1)

    node_wires = set()
    remove_node_wires = set()
    specific_node_wires = set()

    # Create initial node wire pattern
    for node in progressbar.progressbar(raw_node_data):
        if len(node['wires']) <= 1:
            continue

        node_tile, node_wire = node['node'].split('/')

        for wire in node['wires']:
            wire_tile, wire_name = wire['wire'].split('/')

            if node['node'] == wire['wire']:
                assert node_tile == wire_tile
                assert node_wire == wire_name
                gridinfo = grid.gridinfo_at_tilename(node_tile)
                node_wires.add((gridinfo.tile_type, wire_name))

    print(
        'Initial number of wires that are node drivers: {}'.format(
            len(node_wires)))

    # Remove exceptional node wire names, create specific_node_wires set,
    # which is simply the list of wires that are nodes in the graph.
    for node in progressbar.progressbar(raw_node_data):
        if len(node['wires']) <= 1:
            continue

        for wire in node['wires']:
            wire_tile, wire_name = wire['wire'].split('/')
            gridinfo = grid.gridinfo_at_tilename(wire_tile)
            key = gridinfo.tile_type, wire_name

            if node['node'] == wire['wire']:
                assert key in node_wires
            else:
                if key in node_wires:
                    specific_node_wires.add(node['node'])
                    remove_node_wires.add(key)

    # Complete the specific_node_wires list after the pruning of the
    # node_pattern_wires sets.
    for node in progressbar.progressbar(raw_node_data):
        if len(node['wires']) <= 1:
            continue

        for wire in node['wires']:
            wire_tile, wire_name = wire['wire'].split('/')
            gridinfo = grid.gridinfo_at_tilename(wire_tile)
            key = gridinfo.tile_type, wire_name

            if key in remove_node_wires and node['node'] == wire['wire']:
                specific_node_wires.add(node['node'])

    node_wires -= remove_node_wires
    print(
        'Final number of wires that are node drivers: {}'.format(
            len(node_wires)))
    print(
        'Number of wires that are node drivers: {}'.format(
            len(specific_node_wires)))

    # Verify the node wire data.
    for node in progressbar.progressbar(raw_node_data):
        if len(node['wires']) <= 1:
            continue

        found_node_wire = False
        for wire in node['wires']:
            if wire['wire'] in specific_node_wires:
                assert wire['wire'] == node['node']

                found_node_wire = True
                break

        if not found_node_wire:
            for wire in node['wires']:
                wire_tile, wire_name = wire['wire'].split('/')
                gridinfo = grid.gridinfo_at_tilename(wire_tile)
                key = gridinfo.tile_type, wire_name

                if key in node_wires:
                    assert node['node'] == wire['wire']
                else:
                    assert node['node'] != wire['wire']

    # Normalize output.
    tile_types = {}
    for tile_type, tile_wire in node_wires:
        if tile_type not in tile_types:
            tile_types[tile_type] = []

        tile_types[tile_type].append(tile_wire)

    for tile_type in tile_types:
        tile_types[tile_type].sort()

    out = {
        'node_pattern_wires': tile_types,
        'specific_node_wires': sorted(specific_node_wires),
    }

    with open(os.path.join(args.output_dir, 'node_wires.json'), 'w') as f:
        json.dump(out, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
