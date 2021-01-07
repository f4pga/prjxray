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
""" Load tileconn.json and node_wires.json and verify both node names and
node <-> wire mapping against raw node data. """

import argparse
import datetime
import json
import multiprocessing
import os.path
import progressbar
import pyjson5 as json5

from prjxray import util, lib
from prjxray.grid import Grid
from prjxray.connections import Connections
from prjxray.node_model import NodeModel


def read_json5(fname):
    with open(fname, 'r') as f:
        return json5.load(f)


def read_raw_node_data(pool, root_dir):
    """ Read raw node data from root dir. """
    _, nodes = lib.read_root_csv(root_dir)

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

    return raw_node_data


def main():
    parser = argparse.ArgumentParser(
        description="Verify tileconn and node_wires.")
    parser.add_argument('--root_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--max_cpu', type=int, default=10)
    parser.add_argument('--ignored_wires')

    args = parser.parse_args()

    print('{} Reading tilegrid'.format(datetime.datetime.now()))
    with open(os.path.join(util.get_db_root(), util.get_fabric(),
                           'tilegrid.json')) as f:
        tilegrid = json.load(f)
        grid = Grid(db=None, tilegrid=tilegrid)

    print('{} Reading tileconn'.format(datetime.datetime.now()))
    with open(os.path.join(args.output_dir, 'tileconn.json')) as f:
        tileconn = json.load(f)

    print(
        '{} Reading tile wires from tile types'.format(
            datetime.datetime.now()))
    tile_wires = {}
    for f in os.listdir(args.output_dir):
        if f.endswith('.json') and f.startswith('tile_type_'):
            if '_site_type_' in f:
                continue

            tile_type = f[len('tile_type_'):-len('.json')]
            with open(os.path.join(args.output_dir, f)) as fin:
                tile_wires[tile_type] = json.load(fin)['wires']

    connections = Connections(
        tilegrid=tilegrid,
        tileconn=tileconn,
        tile_wires=tile_wires,
    )

    print('{} Reading node wires'.format(datetime.datetime.now()))
    with open(os.path.join(args.output_dir, 'node_wires.json')) as f:
        node_wires = json.load(f)

    print('{} Build initial node model'.format(datetime.datetime.now()))
    node_model = NodeModel(
        grid=grid,
        connections=connections,
        tile_wires=tile_wires,
        node_wires=node_wires,
        progressbar=progressbar.progressbar)

    print('{} Build node model'.format(datetime.datetime.now()))
    nodes = set(node_model.get_nodes())

    print('{} Read raw node data for testing'.format(datetime.datetime.now()))

    processes = min(multiprocessing.cpu_count(), args.max_cpu)
    with multiprocessing.Pool(processes=processes) as pool:
        raw_node_data = read_raw_node_data(pool, args.root_dir)

    print('{} Read ignored wires list'.format(datetime.datetime.now()))
    ignored_wires = []
    ignored_wires_file = args.ignored_wires
    if os.path.exists(ignored_wires_file):
        with open(ignored_wires_file) as f:
            ignored_wires = set(tuple(l.strip().split('/')) for l in f)

    print(
        '{} Verify nodes against raw node data'.format(
            datetime.datetime.now()))
    for node in progressbar.progressbar(raw_node_data):
        tile, wire = node['node'].split('/')

        assert (tile, wire) in nodes
        wires_for_model = node_model.get_wires_for_node(tile, wire)

        wires = set()
        for wire in node['wires']:
            wire_tile, wire_name = wire['wire'].split('/')
            wires.add((wire_tile, wire_name))

        if len(wires) != len(wires_for_model):
            wires2 = set(wires_for_model)
            a_minus_b = wires - wires2
            b_minus_a = wires2 - wires

            assert len(b_minus_a) == 0

            assert len(a_minus_b - ignored_wires) == 0, a_minus_b

        for tile, wire in wires_for_model:
            assert (tile, wire) in wires


if __name__ == '__main__':
    main()
