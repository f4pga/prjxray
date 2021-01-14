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
""" Generate grid from database dump """

from __future__ import print_function
import argparse
import pyjson5 as json5
import multiprocessing
import progressbar
import os.path
import json
import datetime
import pickle
import sys

from prjxray import util, lib
from prjxray.xjson import extract_numbers


def get_tile_grid_info(fname):
    with open(fname, 'r') as f:
        tile = json5.load(f)

    tile_type = tile['type']
    ignored = int(tile['ignored']) != 0

    if ignored:
        tile_type = 'NULL'

    return {
        tile['tile']: {
            'type': tile_type,
            'ignored': ignored,
            'grid_x': tile['x'],
            'grid_y': tile['y'],
            'sites': dict(
                (site['site'], site['type']) for site in tile['sites']),
            'wires': set((wire['wire'] for wire in tile['wires']))
        },
    }


def read_json5(fname):
    with open(fname, 'r') as f:
        return json5.load(f)


def is_edge_shared(edge1, edge2):
    """ Returns true if edge1 or edge2 overlap

  >>> is_edge_shared((0, 1), (0, 1))
  True
  >>> is_edge_shared((0, 2), (0, 1))
  True
  >>> is_edge_shared((0, 1), (0, 2))
  True
  >>> is_edge_shared((1, 2), (0, 3))
  True
  >>> is_edge_shared((0, 3), (1, 2))
  True
  >>> is_edge_shared((1, 2), (0, 2))
  True
  >>> is_edge_shared((0, 2), (1, 2))
  True
  >>> is_edge_shared((0, 2), (1, 3))
  True
  >>> is_edge_shared((1, 3), (0, 2))
  True
  >>> is_edge_shared((0, 1), (1, 2))
  False
  >>> is_edge_shared((1, 2), (0, 1))
  False
  >>> is_edge_shared((0, 1), (2, 3))
  False
  >>> is_edge_shared((2, 3), (0, 1))
  False
  """
    assert edge1[0] < edge1[1], edge1
    assert edge2[0] < edge2[1], edge2

    if edge1[0] <= edge2[0]:
        return edge2[0] < edge1[1]
    else:
        return edge1[0] < edge2[1]


def share_edge(a, b):
    """ Returns true if box defined by a and b share any edge.

  Box is defined as (x-min, y-min, x-max, y-max).

  >>> share_edge((0, 0, 1, 1), (1, 0, 2, 1))
  True
  >>> share_edge((1, 0, 2, 1), (0, 0, 1, 1))
  True
  >>> share_edge((0, 0, 1, 1), (0, 1, 1, 2))
  True
  >>> share_edge((0, 1, 1, 2), (0, 0, 1, 1))
  True
  >>> share_edge((0, 0, 1, 3), (1, 0, 2, 1))
  True
  >>> share_edge((1, 0, 2, 1), (0, 0, 1, 3))
  True
  >>> share_edge((0, 0, 3, 1), (0, 1, 1, 2))
  True
  >>> share_edge((0, 1, 1, 2), (0, 0, 3, 1))
  True
  >>> share_edge((0, 0, 1, 1), (1, 1, 2, 2))
  False
  >>> share_edge((1, 1, 2, 2), (0, 0, 1, 1))
  False
  >>> share_edge((0, 0, 1, 3), (1, 3, 2, 4))
  False
  >>> share_edge((0, 0, 1, 3), (1, 2, 2, 4))
  True
  """

    a_x_min, a_y_min, a_x_max, a_y_max = a
    b_x_min, b_y_min, b_x_max, b_y_max = b

    if a_x_min == b_x_max or a_x_max == b_x_min:
        return is_edge_shared((a_y_min, a_y_max), (b_y_min, b_y_max))
    if a_y_min == b_y_max or a_y_max == b_y_min:
        return is_edge_shared((a_x_min, a_x_max), (b_x_min, b_x_max))


def next_wire_in_dimension(
        wire1, tile1, wire2, tile2, tiles, x_wires, y_wires, wire_map,
        wires_in_node):
    """ next_wire_in_dimension returns true if tile1 and tile2 are in the same
  row and column, and must be adjcent.
  """
    tile1_info = tiles[tile1]
    tile2_info = tiles[tile2]

    tile1_x = tile1_info['grid_x']
    tile2_x = tile2_info['grid_x']
    tile1_y = tile1_info['grid_y']
    tile2_y = tile2_info['grid_y']

    # All wires are in the same row or column or if the each wire lies in its own
    # row or column.
    if len(y_wires) == 1 or len(x_wires) == len(wires_in_node) or abs(
            tile1_y - tile2_y) == 0:
        ordered_wires = sorted(x_wires.keys())

        idx1 = ordered_wires.index(tile1_x)
        idx2 = ordered_wires.index(tile2_x)

        if len(x_wires[tile1_x]) == 1 and len(x_wires[tile2_x]) == 1:
            return abs(idx1 - idx2) == 1

    if len(x_wires) == 1 or len(y_wires) == len(wires_in_node) or abs(
            tile1_x - tile2_x) == 0:
        ordered_wires = sorted(y_wires.keys())

        idx1 = ordered_wires.index(tile1_y)
        idx2 = ordered_wires.index(tile2_y)

        if len(y_wires[tile1_y]) == 1 and len(y_wires[tile2_y]) == 1:
            return abs(idx1 - idx2) == 1

    return None


def only_wire(tile1, tile2, tiles, x_wires, y_wires):
    """ only_wire returns true if tile1 and tile2 only have 1 wire in their respective x or y dimension.
  """
    tile1_info = tiles[tile1]
    tile2_info = tiles[tile2]

    tile1_x = tile1_info['grid_x']
    tile2_x = tile2_info['grid_x']

    tiles_x_adjacent = abs(tile1_x - tile2_x) == 1
    if tiles_x_adjacent and len(x_wires[tile1_x]) == 1 and len(
            x_wires[tile2_x]) == 1:
        return True

    tile1_y = tile1_info['grid_y']
    tile2_y = tile2_info['grid_y']

    tiles_y_adjacent = abs(tile1_y - tile2_y) == 1
    if tiles_y_adjacent and len(y_wires[tile1_y]) == 1 and len(
            y_wires[tile2_y]) == 1:
        return True

    return None


def is_directly_connected(node, node_tree, wire1, wire2):
    if 'wires' in node_tree:
        node_tree_wires = node_tree['wires']
    else:
        if len(node_tree['edges']) == 1 and len(node_tree['joins']) == 0:
            node_tree_wires = node_tree['edges'][0]
        else:
            return None

    if wire1 not in node_tree_wires:
        return None
    if wire2 not in node_tree_wires:
        return None

    # Is there than edge that has wire1 next to wire2?
    for edge in node_tree['edges']:
        idx1 = None
        idx2 = None
        try:
            idx1 = edge.index(wire1)
        except ValueError:
            pass

        try:
            idx2 = edge.index(wire2)
        except ValueError:
            pass

        if idx1 is not None and idx2 is not None:
            return abs(idx1 - idx2) == 1

        if idx1 is not None and (idx1 != 0 and idx1 != len(edge) - 1):
            return False

        if idx2 is not None and (idx2 != 0 and idx2 != len(edge) - 1):
            return False

    # Is there a join of nodes between wire1 and wire2?
    if wire1 in node_tree['joins']:
        return wire2 in node_tree['joins'][wire1]

    if wire2 in node_tree['joins']:
        assert wire1 not in node_tree['joins'][wire2]

    return None


def is_connected(
        wire1, tile1, wire2, tile2, node, wires_in_tiles, wire_map, node_tree,
        tiles, x_wires, y_wires, wires_in_node):
    """ Check if two wires are directly connected. """

    next_wire_in_dim = next_wire_in_dimension(
        wire1, tile1, wire2, tile2, tiles, x_wires, y_wires, wire_map,
        wires_in_node)
    if next_wire_in_dim is not None:
        return next_wire_in_dim

    # Because there are multiple possible wire connections between these two
    # tiles, consult the node_tree to determine if the two wires are actually connected.
    #
    # Warning: The node_tree is incomplete because it is not know how to extract
    # ordered wire information from the node.
    #
    # Example node CLK_BUFG_REBUF_X60Y142/CLK_BUFG_REBUF_R_CK_GCLK0_BOT
    # It does not appear to be possible to get ordered wire connection information
    # for the first two wires connected to PIP
    # CLK_BUFG_REBUF_X60Y117/CLK_BUFG_REBUF.CLK_BUFG_REBUF_R_CK_GCLK0_BOT<<->>CLK_BUFG_REBUF_R_CK_GCLK0_TOP
    #
    # However, it happens to be that theses wires are the only wires in their
    # tiles, so the earlier "only wires in tile" check will pass.

    connected = is_directly_connected(
        node['node'], node_tree[node['node']], wire1, wire2)
    if connected is not None:
        return connected

    is_only_wire = only_wire(tile1, tile2, tiles, x_wires, y_wires)
    if is_only_wire is not None:
        return is_only_wire

    # The node_tree didn't specify these wires, and the wires are not
    # unambiguously connected.
    return False


def process_node(tileconn, key_history, node, wire_map, node_tree, tiles):
    wires = [wire['wire'] for wire in node['wires']]

    wires_in_tiles = {}
    x_wires = {}
    y_wires = {}
    for wire in wires:
        wire_info = wire_map[wire]

        if wire_info['tile'] not in wires_in_tiles:
            wires_in_tiles[wire_info['tile']] = []
        wires_in_tiles[wire_info['tile']].append(wire)

        grid_x = tiles[wire_info['tile']]['grid_x']
        if grid_x not in x_wires:
            x_wires[grid_x] = []
        x_wires[grid_x].append(wire)

        grid_y = tiles[wire_info['tile']]['grid_y']
        if grid_y not in y_wires:
            y_wires[grid_y] = []
        y_wires[grid_y].append(wire)

    if len(wires) == 2:
        wire1 = wires[0]
        wire_info1 = wire_map[wire1]
        wire2 = wires[1]
        wire_info2 = wire_map[wire2]
        update_tile_conn(
            tileconn, key_history, wire1, wire_info1, wire2, wire_info2, tiles)
        return

    for idx, wire1 in enumerate(wires):
        wire_info1 = wire_map[wire1]
        for wire2 in wires[idx + 1:]:
            wire_info2 = wire_map[wire2]

            if not is_connected(wire1, wire_info1['tile'], wire2,
                                wire_info2['tile'], node, wires_in_tiles,
                                wire_map, node_tree, tiles, x_wires, y_wires,
                                wires):
                continue

            update_tile_conn(
                tileconn, key_history, wire1, wire_info1, wire2, wire_info2,
                tiles)


def update_tile_conn(
        tileconn, key_history, wirename1, wire1, wirename2, wire2, tiles):
    # Ensure that (wire1, wire2) is sorted, so we can easy check if a connection
    # already exists.

    tile1 = tiles[wire1['tile']]
    tile2 = tiles[wire2['tile']]
    if ((wire1['type'], wire1['shortname'], tile1['grid_x'], tile1['grid_y']) >
        (wire2['type'], wire2['shortname'], tile2['grid_x'], tile2['grid_y'])):
        wire1, tile1, wire2, tile2 = wire2, tile2, wire1, tile1

    tileconn.append(
        {
            "grid_deltas": [
                tile2['grid_x'] - tile1['grid_x'],
                tile2['grid_y'] - tile1['grid_y'],
            ],
            "tile_types": [
                tile1['type'],
                tile2['type'],
            ],
            "wire_pair": [
                wire1['shortname'],
                wire2['shortname'],
            ],
        })


def flatten_tile_conn(tileconn):
    """ Convert tileconn that is key'd to identify specific wire pairs between tiles
  key (tile1_type, wire1_name, tile2_type, wire2_name) to flat tile connect list
  that relates tile types and relative coordinates and a full list of wires to
  connect. """
    flat_tileconn = {}

    for conn in tileconn:
        key = (tuple(conn['tile_types']), tuple(conn['grid_deltas']))

        if key not in flat_tileconn:
            flat_tileconn[key] = {
                'tile_types': conn['tile_types'],
                'grid_deltas': conn['grid_deltas'],
                'wire_pairs': set()
            }

        flat_tileconn[key]['wire_pairs'].add(tuple(conn['wire_pair']))

    def inner():
        for output in flat_tileconn.values():
            yield {
                'tile_types': output['tile_types'],
                'grid_deltas': output['grid_deltas'],
                'wire_pairs': tuple(output['wire_pairs']),
            }

    return tuple(inner())


def is_tile_type(tiles, coord_to_tile, coord, tile_type):
    if coord not in coord_to_tile:
        return False

    target_tile = tiles[coord_to_tile[coord]]
    return target_tile['type'] == tile_type


def get_connections(wire, wire_info, conn, idx, coord_to_tile, tiles):
    """ Yields (tile_coord, wire) for each wire that should be connected to specified wire. """
    pair = conn['wire_pairs'][idx]
    wire_tile_type = wire_info['type']
    tile_types = conn['tile_types']
    shortname = wire_info['shortname']
    grid_deltas = conn['grid_deltas']

    wire1 = tile_types[0] == wire_tile_type and shortname == pair[0]
    wire2 = tile_types[1] == wire_tile_type and shortname == pair[1]
    assert wire1 or wire2, (wire, conn)

    tile_of_wire = wire_info['tile']
    start_coord_x = tiles[tile_of_wire]['grid_x']
    start_coord_y = tiles[tile_of_wire]['grid_y']
    if wire1:
        target_coord_x = start_coord_x + grid_deltas[0]
        target_coord_y = start_coord_y + grid_deltas[1]
        target_tile_type = tile_types[1]

        target_wire = pair[1]
        target_tile = (target_coord_x, target_coord_y)

        if is_tile_type(tiles, coord_to_tile, target_tile, target_tile_type):
            yield target_tile, target_wire

    if wire2:
        target_coord_x = start_coord_x - grid_deltas[0]
        target_coord_y = start_coord_y - grid_deltas[1]
        target_tile_type = tile_types[0]

        target_wire = pair[0]
        target_tile = (target_coord_x, target_coord_y)

        if is_tile_type(tiles, coord_to_tile, target_tile, target_tile_type):
            yield target_tile, target_wire


def make_connection(wire_nodes, wire1, wire2):
    if wire_nodes[wire1] is wire_nodes[wire2]:
        assert wire1 in wire_nodes[wire1]
        assert wire2 in wire_nodes[wire2]
        return

    new_node = wire_nodes[wire1] | wire_nodes[wire2]

    for wire in new_node:
        wire_nodes[wire] = new_node


def create_coord_to_tile(tiles):
    coord_to_tile = {}
    for tile, tileinfo in tiles.items():
        coord_to_tile[(tileinfo['grid_x'], tileinfo['grid_y'])] = tile

    return coord_to_tile


def connect_wires(tiles, tileconn, wire_map):
    """ Connect individual wires into groups of wires called nodes. """

    # Initialize all nodes to originally only contain the wire by itself.
    wire_nodes = {}
    for wire in wire_map:
        wire_nodes[wire] = set([wire])

    wire_connection_map = {}
    for conn in tileconn:
        for idx, (wire1, wire2) in enumerate(conn['wire_pairs']):
            key1 = (conn['tile_types'][0], wire1)
            if key1 not in wire_connection_map:
                wire_connection_map[key1] = []
            wire_connection_map[key1].append((conn, idx))

            key2 = (conn['tile_types'][1], wire2)
            if key2 not in wire_connection_map:
                wire_connection_map[key2] = []
            wire_connection_map[key2].append((conn, idx))

    coord_to_tile = create_coord_to_tile(tiles)

    for wire, wire_info in progressbar.progressbar(wire_map.items()):
        key = (wire_info['type'], wire_info['shortname'])
        if key not in wire_connection_map:
            continue

        for conn, idx in wire_connection_map[key]:
            for target_tile, target_wire in get_connections(
                    wire, wire_info, conn, idx, coord_to_tile, tiles):

                full_wire_name = coord_to_tile[target_tile] + '/' + target_wire
                assert wire_map[full_wire_name]['shortname'] == target_wire, (
                    target_tile, target_wire, wire, conn)
                assert wire_map[full_wire_name]['tile'] == coord_to_tile[
                    target_tile], (
                        wire_map[full_wire_name]['tile'],
                        coord_to_tile[target_tile])

                make_connection(wire_nodes, wire, full_wire_name)

    # Find unique nodes
    nodes = {}
    for node in wire_nodes.values():
        nodes[id(node)] = node

    # Flatten to list of lists.
    return tuple(tuple(node) for node in nodes.values())


def generate_tilegrid(pool, tiles):
    wire_map = {}

    grid = {}

    num_tiles = 0
    for tile_type in tiles:
        num_tiles += len(tiles[tile_type])

    idx = 0
    with progressbar.ProgressBar(max_value=num_tiles) as bar:
        for tile_type in tiles:
            for tile in pool.imap_unordered(
                    get_tile_grid_info,
                    tiles[tile_type],
                    chunksize=20,
            ):
                bar.update(idx)

                assert len(tile) == 1, tile
                tilename = tuple(tile.keys())[0]

                for wire in tile[tilename]['wires']:
                    assert wire not in wire_map, (wire, wire_map)
                    assert wire.startswith(tilename + '/'), (wire, tilename)

                    wire_map[wire] = {
                        'tile': tilename,
                        'type': tile[tilename]['type'],
                        'shortname': wire[len(tilename) + 1:],
                    }

                del tile[tilename]['wires']
                grid.update(tile)

                idx += 1
                bar.update(idx)

    return grid, wire_map


def generate_tileconn(pool, node_tree, nodes, wire_map, grid):
    tileconn = []
    key_history = {}
    raw_node_data = []
    with progressbar.ProgressBar(max_value=len(nodes)) as bar:
        for idx, node in enumerate(pool.imap_unordered(
                read_json5,
                nodes,
                chunksize=20,
        )):
            bar.update(idx)
            raw_node_data.append(node)
            process_node(
                tileconn, key_history, node, wire_map, node_tree, grid)
            bar.update(idx + 1)

    tileconn = flatten_tile_conn(tileconn)

    return tileconn, raw_node_data


def main():
    parser = argparse.ArgumentParser(
        description=
        "Reduces raw database dump into prototype tiles, grid, and connections."
    )
    parser.add_argument('--root_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--verify_only', action='store_true')
    parser.add_argument('--ignored_wires')
    parser.add_argument('--max_cpu', type=int, default=10)

    args = parser.parse_args()

    tiles, nodes = lib.read_root_csv(args.root_dir)

    processes = min(multiprocessing.cpu_count(), args.max_cpu)
    print('{} Running {} processes'.format(datetime.datetime.now(), processes))
    pool = multiprocessing.Pool(processes=processes)

    node_tree_file = os.path.join(args.output_dir, 'node_tree.json')

    tileconn_file = os.path.join(args.output_dir, 'tileconn.json')
    wire_map_file = os.path.join(args.output_dir, 'wiremap.pickle')

    print('{} Reading tilegrid'.format(datetime.datetime.now()))
    with open(os.path.join(util.get_db_root(), util.get_fabric(),
                           'tilegrid.json')) as f:
        grid = json.load(f)

    if not args.verify_only:
        print('{} Creating tile map'.format(datetime.datetime.now()))
        grid2, wire_map = generate_tilegrid(pool, tiles)

        # Make sure tilegrid from 005-tilegrid matches tilegrid from
        # generate_tilegrid.
        db_grid_keys = set(grid.keys())
        generated_grid_keys = set(grid2.keys())
        assert db_grid_keys == generated_grid_keys, (
            db_grid_keys ^ generated_grid_keys)

        for tile in db_grid_keys:
            for k in grid2[tile]:
                if k == 'ignored':
                    continue

                if k == 'sites' and grid2[tile]['ignored']:
                    continue

                assert k in grid[tile], k
                assert grid[tile][k] == grid2[tile][k], (
                    tile, k, grid[tile][k], grid2[tile][k])

        with open(wire_map_file, 'wb') as f:
            pickle.dump(wire_map, f)

        print('{} Reading node tree'.format(datetime.datetime.now()))
        with open(node_tree_file) as f:
            node_tree = json.load(f)

        print('{} Creating tile connections'.format(datetime.datetime.now()))
        tileconn, raw_node_data = generate_tileconn(
            pool, node_tree, nodes, wire_map, grid)

        for data in tileconn:
            data['wire_pairs'] = tuple(
                sorted(
                    data['wire_pairs'],
                    key=lambda x: tuple(extract_numbers(s) for s in x)))

        tileconn = tuple(
            sorted(
                tileconn, key=lambda x: (x['tile_types'], x['grid_deltas'])))

        print('{} Writing tileconn'.format(datetime.datetime.now()))
        with open(tileconn_file, 'w') as f:
            json.dump(tileconn, f, indent=2, sort_keys=True)
    else:
        with open(wire_map_file, 'rb') as f:
            wire_map = pickle.load(f)

        print('{} Reading raw_node_data'.format(datetime.datetime.now()))
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

        print('{} Reading tileconn'.format(datetime.datetime.now()))
        with open(tileconn_file) as f:
            tileconn = json.load(f)

    wire_nodes_file = os.path.join(args.output_dir, 'wire_nodes.pickle')
    if os.path.exists(wire_nodes_file) and args.verify_only:
        with open(wire_nodes_file, 'rb') as f:
            wire_nodes = pickle.load(f)
    else:
        print(
            "{} Connecting wires to verify tileconn".format(
                datetime.datetime.now()))
        wire_nodes = connect_wires(grid, tileconn, wire_map)
        with open(wire_nodes_file, 'wb') as f:
            pickle.dump(wire_nodes, f)

    print('{} Verifing tileconn'.format(datetime.datetime.now()))
    error_nodes = []
    lib.verify_nodes(
        [
            (node['node'], tuple(wire['wire']
                                 for wire in node['wires']))
            for node in raw_node_data
        ], wire_nodes, error_nodes)

    if len(error_nodes) > 0:
        error_nodes_file = os.path.join(args.output_dir, 'error_nodes.json')
        with open(error_nodes_file, 'w') as f:
            json.dump(error_nodes, f, indent=2, sort_keys=True)

        ignored_wires = []
        ignored_wires_file = args.ignored_wires
        if os.path.exists(ignored_wires_file):
            with open(ignored_wires_file) as f:
                ignored_wires = set(l.strip() for l in f)

        if not lib.check_errors(error_nodes, ignored_wires):
            print(
                '{} errors detected, see {} for details.'.format(
                    len(error_nodes), error_nodes_file))
            sys.exit(1)
        else:
            print(
                '{} errors ignored because of {}\nSee {} for details.'.format(
                    len(error_nodes), ignored_wires_file, error_nodes_file))


if __name__ == '__main__':
    main()
