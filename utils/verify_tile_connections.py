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
from __future__ import print_function
import prjxray.db
import prjxray.lib
import argparse
import datetime
import progressbar
import multiprocessing
import pyjson5 as json5
import json
import sys
from prjxray.util import OpenSafeFile, db_root_arg, part_arg


def full_wire_name(wire_in_grid):
    return '{}/{}'.format(wire_in_grid.tile, wire_in_grid.wire)


def make_connection(wires, connection):
    wire_a = full_wire_name(connection.wire_a)
    wire_b = full_wire_name(connection.wire_b)

    if wire_a not in wires:
        wires[wire_a] = set((wire_a, ))

    if wire_b not in wires:
        wires[wire_b] = set((wire_b, ))

    wire_a_set = wires[wire_a]
    wire_b_set = wires[wire_b]

    if wire_a_set is wire_b_set:
        return

    wire_a_set |= wire_b_set

    for wire in wire_a_set:
        wires[wire] = wire_a_set


def make_connections(db_root, part):
    db = prjxray.db.Database(db_root, part)
    c = db.connections()

    wires = {}
    for connection in c.get_connections():
        make_connection(wires, connection)

    nodes = {}

    for wire_node in wires.values():
        nodes[id(wire_node)] = wire_node

    return nodes.values()


def read_json5(fname):
    with OpenSafeFile(fname, 'r') as f:
        return json5.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Tests database against raw node list.")

    db_root_arg(parser)
    part_arg(parser)
    parser.add_argument('--raw_node_root', required=True)
    parser.add_argument('--error_nodes', default="error_nodes.json")
    parser.add_argument('--ignored_wires')

    args = parser.parse_args()

    processes = min(multiprocessing.cpu_count(), 10)

    print('{} Running {} processes'.format(datetime.datetime.now(), processes))
    pool = multiprocessing.Pool(processes=processes)
    print(
        '{} Reading raw data index'.format(datetime.datetime.now(), processes))
    _, nodes = prjxray.lib.read_root_csv(args.raw_node_root)
    print('{} Reading raw_node_data'.format(datetime.datetime.now()))
    raw_node_data = []
    with progressbar.ProgressBar(max_value=len(nodes)) as bar:
        for idx, node in enumerate(pool.imap_unordered(
                read_json5,
                nodes,
                chunksize=20,
        )):
            bar.update(idx)
            raw_node_data.append(
                (node['node'], tuple(wire['wire'] for wire in node['wires'])))
            bar.update(idx + 1)

    print('{} Creating connections'.format(datetime.datetime.now()))
    generated_nodes = make_connections(args.db_root, args.part)

    print('{} Verifying connections'.format(datetime.datetime.now()))
    error_nodes = []
    prjxray.lib.verify_nodes(raw_node_data, generated_nodes, error_nodes)

    if len(error_nodes) > 0:
        if args.ignored_wires:
            with OpenSafeFile(args.ignored_wires, 'r') as f:
                ignored_wires = [l.strip() for l in f.readlines()]

        print(
            '{} Found {} errors, writing errors to {}'.format(
                datetime.datetime.now(),
                len(error_nodes),
                args.error_nodes,
            ))

        with OpenSafeFile(args.error_nodes, 'w') as f:
            json.dump(error_nodes, f, indent=2)

        if not args.ignored_wires:
            sys.exit(1)

        if not prjxray.lib.check_errors(error_nodes, ignored_wires):
            print(
                '{} Errors were not ignored via ignored_wires {}'.format(
                    datetime.datetime.now(),
                    args.ignored_wires,
                ))
            sys.exit(1)
        else:
            print(
                '{} All errors were via ignored_wires {}'.format(
                    datetime.datetime.now(),
                    args.ignored_wires,
                ))


if __name__ == '__main__':
    main()
