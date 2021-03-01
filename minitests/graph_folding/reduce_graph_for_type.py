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

import argparse
import time
from collections import namedtuple
import progressbar
import capnp
import capnp.lib.capnp
capnp.remove_import_hook()
import math
import json
import re
from distributed_bsc import BipartiteAdjacencyMatrix, find_bsc_par, \
        greedy_set_cover_with_complete_bipartite_subgraphs, \
        greed_set_cover_par
import gc
import multiprocessing
<<<<<<< HEAD
=======
from reference_model import CompactArray, StructOfArray
import os.path
from bokeh_plotting import create_plot_from_graph
from bitarray import bitarray
>>>>>>> 7bf2be5c... All changed for max shared algorithm. The code is not yet complete, but this is just a work in progress.

from prjxray.node_lookup import NodeLookup

Tile = namedtuple('Tile', 'tile_pkey')
WireToNode = namedtuple(
    'WireToNode', 'wire_in_tile_pkey delta_x delta_y node_wire_in_tile_pkey')
NodeToWire = namedtuple('NodeToWire', 'wire_in_tile_pkey delta_x delta_y has_pip_from')

all_info = {}

use_ms = True # Determines whether or not you are using the max_shared algorithm
use_gs = False # Determines whether or not you are using greedy_set cover
use_prints = {"size_on_disk": False,
              "printCapnp"  : False,
              "printSubgraphNones": False,
              "needed_combinations": False,
              "density": False,
              "ms_runtime": False,
              "write_to_type": True,
              "processing_build": False}

use_progressbar = False # print out progressbar or not

def print_and_json(input_string):
    global all_info
    all_info[input_string.split(':')[0]] = ''.join(input_string.split(':')[1:])

def get_wire_to_node_graph(database, tile_type):
    lookup = NodeLookup(database=database)
    cur = lookup.conn.cursor()
    cur2 = lookup.conn.cursor()
    cur3 = lookup.conn.cursor()

    all_tiles = set()
    all_wire_to_nodes = set()

    graph = BipartiteAdjacencyMatrix()

    cur.execute("SELECT pkey FROM tile_type WHERE name = ?;", (tile_type, ))
    tile_type_pkey = cur.fetchone()[0]

    global use_progressbar
    iterator = progressbar.progressbar(
            cur.execute(
                "SELECT pkey, tile_type_pkey, name, x, y FROM tile WHERE tile_type_pkey = ?;",
                (tile_type_pkey, ))) if use_progressbar else cur.execute(
                "SELECT pkey, tile_type_pkey, name, x, y FROM tile WHERE tile_type_pkey = ?;",
                (tile_type_pkey, ))
    for tile_pkey, tile_type_pkey, tile_name, tile_x, tile_y in iterator:
        tile = Tile(tile_pkey=tile_pkey)
        graph.add_u(tile)
        all_tiles.add(tile)

        for wire_in_tile_pkey, wire_pkey, node_pkey in cur2.execute("""
SELECT wire_in_tile_pkey, wire.pkey, wire.node_pkey
FROM wire
WHERE tile_pkey = ?;
                """, (tile_pkey, )):
            cur3.execute(
                """
SELECT tile.x, tile.y, node.wire_in_tile_pkey
FROM node
INNER JOIN tile ON node.tile_pkey = tile.pkey
WHERE node.pkey = ?;
                """, (node_pkey, ))
            node_tile_x, node_tile_y, node_wire_in_tile_pkey = cur3.fetchone()

            delta_x = node_tile_x - tile_x
            delta_y = node_tile_y - tile_y

            if delta_x == 0 and delta_y == 0 and wire_in_tile_pkey == node_wire_in_tile_pkey:
                continue

            pattern = WireToNode(
                wire_in_tile_pkey=wire_in_tile_pkey,
                delta_x=delta_x,
                delta_y=delta_y,
                node_wire_in_tile_pkey=node_wire_in_tile_pkey)

            if pattern not in all_wire_to_nodes:
                all_wire_to_nodes.add(pattern)
                graph.add_v(pattern)

            graph.add_edge(tile, pattern)

    graph.build()

    
    # create_plot_from_graph(graph)
    return graph


def get_node_to_wires_graph(database, tile_type):
    lookup = NodeLookup(database=database)
    cur = lookup.conn.cursor()
    cur2 = lookup.conn.cursor()
    cur3 = lookup.conn.cursor()

    all_tiles = set()
    all_node_to_wires = set()

    graph = BipartiteAdjacencyMatrix()

    cur.execute("SELECT pkey FROM tile_type WHERE name = ?;", (tile_type, ))
    tile_type_pkey = cur.fetchone()[0]

<<<<<<< HEAD
    for tile_pkey, tile_type_pkey, tile_name, tile_x, tile_y in progressbar.progressbar(
=======
    if only_pips:
        extra_conditions = " AND wire_in_tile.has_pip_from"  # Only including wire if it is the ending of a set of wires
    else:
        extra_conditions = ""
    global use_progressbar
    iterator = progressbar.progressbar(  # add tiles to the graph as u's
>>>>>>> 7bf2be5c... All changed for max shared algorithm. The code is not yet complete, but this is just a work in progress.
            cur.execute(
                "SELECT pkey, tile_type_pkey, name, x, y FROM tile WHERE tile_type_pkey = ?;",
                (tile_type_pkey, ))) if use_progressbar else cur.execute(
                "SELECT pkey, tile_type_pkey, name, x, y FROM tile WHERE tile_type_pkey = ?;",
                (tile_type_pkey, ))
    for tile_pkey, tile_type_pkey, tile_name, tile_x, tile_y in iterator:
        tile = Tile(tile_pkey=tile_pkey)
        graph.add_u(tile)
        all_tiles.add(tile)

        # rint(f'tile_pkey: {tile_pkey}')
        #iterate over every node of every tile
        for node_pkey, node_wire_in_tile_pkey in cur2.execute("""
SELECT node.pkey, node.wire_in_tile_pkey
FROM node
WHERE node.tile_pkey = ?;
            """, (tile_pkey, )):

            # rint(f'    node_pkey: {node_pkey} and wire_in_tile_pkey(starting wire_pkey): {node_wire_in_tile_pkey}')
            node_to_wires = []  # create an empty list for each node

            # grab the x and y values of the tile that the wire is in. This is the ending wire. The first one is the node's one.
            # so...wire_tile_x is the ending x value, and tile_x is the starting x value
            for wire_in_tile_pkey, wire_tile_x, wire_tile_y, wire_has_pip_from in cur3.execute("""
SELECT wire.wire_in_tile_pkey, tile.x, tile.y, wire_in_tile.has_pip_from
FROM wire
INNER JOIN tile ON wire.tile_pkey = tile.pkey
INNER JOIN wire_in_tile ON wire.wire_in_tile_pkey = wire_in_tile.pkey
WHERE wire.node_pkey = ? and wire_in_tile.has_pip_from;
                """, (node_pkey, )):

                delta_x = wire_tile_x - tile_x  # compute the difference from start to end of a node
                delta_y = wire_tile_y - tile_y
                # rint(f'        wire_in_tile_pkey(ending wire_pkey): {wire_in_tile_pkey}, delta_x: {delta_x}, delta_y: {delta_y}, node_pkey: {node_pkey}')
                if delta_x == 0 and delta_y == 0 and wire_in_tile_pkey == node_wire_in_tile_pkey:  # if there is no difference, and they share a primary key, just continue
                    continue

                node_to_wires.append(
                    NodeToWire(
                        delta_x=delta_x,
                        delta_y=delta_y,
                        wire_in_tile_pkey=wire_in_tile_pkey,
                        has_pip_from=wire_has_pip_from))

            if len(node_to_wires) == 0:
                continue

            node_to_wires = (node_wire_in_tile_pkey, frozenset(node_to_wires))  # (starting tile pkey, ending delta options?)
            if node_to_wires not in all_node_to_wires:
                all_node_to_wires.add(node_to_wires)
                graph.add_v(node_to_wires)

            graph.add_edge(tile, node_to_wires)

    graph.build()
    
    # create_plot_from_graph(graph, tile_type)
    
    return graph


<<<<<<< HEAD
def main():
    multiprocessing.set_start_method('spawn')
=======
def write_wire_to_node(
        graph, required_solutions, tile_patterns, tile_to_tile_patterns,
        output_dir, tile_type, cover_method):
    global use_prints
    
    if use_prints['write_to_type']:
        print(f"                            {tile_type}     Wire to node    {cover_method}")

    wire_in_tile_pkeys = set()
    all_node_patterns = set()

    for pattern in graph.v:
        wire_in_tile_pkeys.add(pattern.wire_in_tile_pkey)
        all_node_patterns.add(
            (pattern.delta_x, pattern.delta_y, pattern.node_wire_in_tile_pkey))

    wire_in_tile_pkeys_data = CompactArray()
    wire_in_tile_pkeys_data.set_items(sorted(wire_in_tile_pkeys))

    node_patterns = StructOfArray(
        'WireToNodePattern', ('delta_x', 'delta_y', 'node_wire_in_tile_pkey'))
    node_patterns.set_items(sorted(all_node_patterns))

    subgraphs = []
    subgraphs_null_count = []
    subgraph_idx_to_tiles = {}

    for subgraph_idx, (tiles, patterns) in enumerate(required_solutions):
        subgraph_idx_to_tiles[subgraph_idx] = tiles

        subgraph = CompactArray()
        subgraph.init_items(len(wire_in_tile_pkeys))

        for pattern in patterns:
            idx = wire_in_tile_pkeys_data.index(pattern.wire_in_tile_pkey)
            subgraph.items[idx] = node_patterns.index(
                (
                    pattern.delta_x, pattern.delta_y,
                    pattern.node_wire_in_tile_pkey))

        null_count = 0
        for item in subgraph.items:
            if item is None:
                null_count += 1

        subgraphs.append(subgraph)
        subgraphs_null_count.append(null_count)

    tile_patterns_data = []
    tile_pattern_to_index = {}
    tile_patterns = sorted(tile_patterns)
    for idx, tile_pattern in enumerate(tile_patterns):
        tile_pattern_to_index[tile_pattern] = idx
        tile_pattern_data = CompactArray()

        # Have tile patterns put more complete subgraphs earlier than later.
        tile_pattern_data.set_items(
            sorted(tile_pattern, key=lambda x: subgraphs_null_count[x]))
        tile_patterns_data.append(tile_pattern_data)
>>>>>>> 7bf2be5c... All changed for max shared algorithm. The code is not yet complete, but this is just a work in progress.

    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    parser.add_argument('--tile', required=True)
    parser.add_argument('--wire_to_node', action='store_true')
    parser.add_argument('--node_to_wires', action='store_true')

    args = parser.parse_args()

    if args.wire_to_node and args.node_to_wires:
        parser.error('Cannot supply both --wire_to_node and --node_to_wires')
    elif not args.wire_to_node and not args.node_to_wires:
        parser.error('Must supply --wire_to_node or --node_to_wires')

    if args.wire_to_node:
        graph = get_wire_to_node_graph(args.database, args.tile)
    elif args.node_to_wires:
        graph = get_node_to_wires_graph(args.database, args.tile)
    else:
        assert False

<<<<<<< HEAD
    all_edges = set(graph.frozen_edges)
    gc.collect()

=======
                wire_in_tile_pkey = wire_in_tile_pkeys_data.items[wire_idx]
                pattern = node_patterns.get(node_pattern_idx)

                pattern_tup = WireToNode(
                    wire_in_tile_pkey=wire_in_tile_pkey,
                    delta_x=pattern['delta_x'],
                    delta_y=pattern['delta_y'],
                    node_wire_in_tile_pkey=pattern['node_wire_in_tile_pkey'],
                )

                assert graph.is_edge(tile, pattern_tup)

    tile_to_tile_patterns = StructOfArray(
        'TileToTilePatterns', ('tile_pkey', 'tile_pattern_index'))
    tile_to_tile_patterns.set_items(sorted(tile_to_tile_patterns_data))

    graph_storage_schema = capnp.load('graph_storage.capnp')
    ms_graph_storage_schema = capnp.load('max_shared_storage.capnp')
    wire_to_nodes = graph_storage_schema.WireToNodeStorage.new_message()

    wire_in_tile_pkeys_data.write_to_capnp(wire_to_nodes.wireInTilePkeys)
    node_patterns.write_to_capnp(
        (
            wire_to_nodes.nodePatternDx,
            wire_to_nodes.nodePatternDy,
            wire_to_nodes.nodePatternToNodeWire,
        ))

    subgraphs_capnp = wire_to_nodes.init('subgraphs', len(subgraphs))
    for subgraph_capnp, subgraph in zip(subgraphs_capnp, subgraphs):
        subgraph.write_to_capnp(subgraph_capnp)

    tile_patterns_capnp = wire_to_nodes.init(
        'tilePatterns', len(tile_patterns_data))
    for tile_pattern_capnp, tile_pattern in zip(tile_patterns_capnp,
                                                tile_patterns_data):
        tile_pattern.write_to_capnp(tile_pattern_capnp)

    tile_to_tile_patterns.write_to_capnp(
        (wire_to_nodes.tilePkeys, wire_to_nodes.tileToTilePatterns))

    serialized = wire_to_nodes.to_bytes()
    print('Size on disk: ', len(serialized))

    def printCapnp(wire_to_nodes):
        global use_prints
        if use_prints["printCapnp"]:
            w2n = str(wire_to_nodes)
            all_pattern = """(?:storage.*?= )(\[.*?\])|(wireInTilePkeys|nodePatternDx|nodePatternDy|
                                nodePatternToNodeWire|tilePatterns|tilePkeys|tileToTilePatterns|subgraphs)"""
            regex_result = re.findall(all_pattern, w2n, re.DOTALL)
            for cur_result in regex_result:
                for this_result in cur_result:
                    print(this_result.replace(',', '\n'))
            print(regex_result)



    if output_dir:
        with open(os.path.join(output_dir,
                               '{}_wire_to_nodes.bin'.format(tile_type)),
                  'wb') as f:
            f.write(serialized)
    printCapnp(wire_to_nodes)
    return len(serialized), wire_to_nodes



def write_node_to_wires(
        graph, required_solutions, tile_patterns, tile_to_tile_patterns,
        output_dir, tile_type, only_pips, cover_method):
    global use_prints

    if use_prints['write_to_type']:
        if only_pips:
            print(f"                        {tile_type}     Node to wires (only pips)   {cover_method}")
        else:
            print(f"                        {tile_type}     Node to wires   {cover_method}")

    if cover_method == 'greedy_set':
        node_wire_in_tile_pkeys = set()
        all_wire_patterns = set()

        graph_storage_schema = capnp.load('graph_storage.capnp')
        gs_node_to_wires = graph_storage_schema.NodeToWiresStorage.new_message()



        for node_wire_in_tile_pkey, node_to_wires in graph.v: # for every v
            node_wire_in_tile_pkeys.add(node_wire_in_tile_pkey)

            for pattern in node_to_wires: # for every pattern in every v
                all_wire_patterns.add( # once this for loop is done, all_wire_patterns will have every pattern in it
                    (pattern.delta_x, pattern.delta_y, pattern.wire_in_tile_pkey))

        node_wire_in_tile_pkeys_array = CompactArray()
        node_wire_in_tile_pkeys_array.set_items(sorted(node_wire_in_tile_pkeys))

        wire_patterns = StructOfArray(
            "NodeToWirePattern", ('delta_x', 'delta_y', 'wire_in_tile_pkey'))
        wire_patterns.set_items(sorted(all_wire_patterns))

        node_patterns_to_idx = {}
        node_patterns_data = []
        for _, node_patterns in required_solutions:
            for _, patterns in node_patterns:
                if patterns in node_patterns_to_idx:
                    continue

                node_patterns_to_idx[patterns] = len(node_patterns_data)
                node_patterns_data.append(CompactArray())

                node_patterns = []
                for pattern in patterns:
                    key = (
                        pattern.delta_x, pattern.delta_y,
                        pattern.wire_in_tile_pkey)
                    assert key in all_wire_patterns
                    node_patterns.append(wire_patterns.index(key))
                node_patterns_data[-1].set_items(sorted(node_patterns))

        subgraphs = []
        subgraphs_null_count = []

        for tile_pkeys, node_patterns in required_solutions:
            subgraph = CompactArray()
            subgraph.init_items(len(node_wire_in_tile_pkeys))

            for node_wire_in_tile_pkey, node_patterns in node_patterns: # these are the vs (node_patterns)
                idx = node_wire_in_tile_pkeys_array.index(node_wire_in_tile_pkey)
                if node_patterns_to_idx[node_patterns] is not None:
                    subgraph.items[idx] = node_patterns_to_idx[node_patterns]

            null_count = 0
            for item in subgraph.items:
                if item is None:
                    null_count += 1
            # subgraph.items = list(filter((None).__ne__, subgraph.items))# use this line to get smaller files by removing the null items
            subgraphs.append(subgraph)
            subgraphs_null_count.append(null_count)

        print(f'{cover_method} null count: {subgraphs_null_count}')
        tile_patterns_data = []
        tile_pattern_to_index = {}
        for idx, tile_pattern in enumerate(tile_patterns):
            tile_pattern_to_index[tile_pattern] = idx
            tile_pattern_data = CompactArray()

            # Have tile patterns put more complete subgraphs earlier than later.
            tile_pattern_data.set_items(
                sorted(tile_pattern, key=lambda x: -subgraphs_null_count[x]))
            tile_patterns_data.append(tile_pattern_data)

        tile_to_tile_patterns_data = []
        for tile, tile_pattern in tile_to_tile_patterns.items():
            tile_to_tile_patterns_data.append(
                (tile.tile_pkey, tile_pattern_to_index[tile_pattern]))

        tile_to_tile_patterns = StructOfArray(
            'TileToTilePatterns', ('tile_pkey', 'tile_pattern_index'))
        tile_to_tile_patterns.set_items(sorted(tile_to_tile_patterns_data))




        # write nodeWireInTilePkeys
        node_wire_in_tile_pkeys_array.write_to_capnp(
            gs_node_to_wires.nodeWireInTilePkeys)

        # write wirePatternDx, wirePatternDy, wirePatternToWire
        wire_patterns.write_to_capnp(
            (
                gs_node_to_wires.wirePatternDx,
                gs_node_to_wires.wirePatternDy,
                gs_node_to_wires.wirePatternToWire,
            ))

        # init nodePatterns list
        node_patterns_capnp = gs_node_to_wires.init(
            'nodePatterns', len(node_patterns_data))
        # write nodePatterns
        for node_pattern_capnp, node_pattern in zip(node_patterns_capnp,
                                                    node_patterns_data):
            node_pattern.write_to_capnp(node_pattern_capnp)
        # init subgraphs list
        subgraphs_capnp = gs_node_to_wires.init('subgraphs', len(subgraphs))
        # write subgraphs
        for subgraph_capnp, subgraph in zip(subgraphs_capnp, subgraphs):
            subgraph.write_to_capnp(subgraph_capnp)

        # init tilePatterns list
        tile_patterns_capnp = gs_node_to_wires.init(
            'tilePatterns', len(tile_patterns_data))
        # write tilePatterns
        for tile_pattern_capnp, tile_pattern in zip(tile_patterns_capnp,
                                                    tile_patterns_data):
            tile_pattern.write_to_capnp(tile_pattern_capnp)

        # write tileToTilePatterns
        tile_to_tile_patterns.write_to_capnp(
            (gs_node_to_wires.tilePkeys, gs_node_to_wires.tileToTilePatterns))
        
        final_node_to_wires = gs_node_to_wires


    if cover_method == 'max_shared':
        ms_graph_storage_schema = capnp.load('max_shared_storage.capnp')
        ms_nodes_and_wires = ms_graph_storage_schema.NodesAndWiresStorage.new_message()

        # get tilePkeys
        ms_tilePkeys = []
        for tile in graph.u:
            ms_tilePkeys.append(tile.tile_pkey)
        ms_tilePkeys = sorted(ms_tilePkeys)
        
        #get nodeWireInTilePkeys
        ms_nodeWireInTilePkeys = []
        for v in graph.v:
            ms_nodeWireInTilePkeys.append(v[0])
        ms_nodeWireInTilePkeys = sorted(list(set(ms_nodeWireInTilePkeys))) #remove duplicates and order them

        #create tilePatterns
        ms_tilePatterns = []
        ms_tile_patterns_capnp = []
        for i in range(len(ms_tilePkeys)): # create empty list of lists (one for each tile)
             ms_tilePatterns.append([])
             
        ms_subgraphs, ms_wirePatternDx, ms_wirePatternDy, ms_wirePatternToWire = [], [], [], []

        ms_subgraphs_capnp, ms_wirePatternDx_capnp, ms_wirePatternDy_capnp, ms_wirePatternToWire_capnp = [], [], [], []

        for i in range(len(required_solutions)): # create empty list of lists of subgraph, dx, dy, and wirePatternToWire (one for each subgraph)
            ms_subgraphs.append([])
            ms_wirePatternDx.append([])
            ms_wirePatternDy.append([])
            ms_wirePatternToWire.append([])
        for subgraph_idx, solution in enumerate(required_solutions):
            for wirePattern in solution[1]:
                cur_nodeWireInTilePkey = wirePattern[0]
                for dx_dy_pkey in wirePattern[1]:
                    ms_subgraphs[subgraph_idx].append(ms_nodeWireInTilePkeys.index(cur_nodeWireInTilePkey)) # add the nodeWireInTilePkey to the current subgraph
                    ms_wirePatternDx[subgraph_idx].append(dx_dy_pkey.delta_x)
                    ms_wirePatternDy[subgraph_idx].append(dx_dy_pkey.delta_y)
                    ms_wirePatternToWire[subgraph_idx].append(dx_dy_pkey.wire_in_tile_pkey)
            subgraph_array, dx_array, dy_array, wirePattern_array = CompactArray(), CompactArray(), CompactArray(), CompactArray()
            subgraph_array.set_items(ms_subgraphs[subgraph_idx])
            dx_array.set_items(ms_wirePatternDx[subgraph_idx])
            dy_array.set_items(ms_wirePatternDy[subgraph_idx])
            wirePattern_array.set_items(ms_wirePatternToWire[subgraph_idx])

            ms_subgraphs_capnp.append(subgraph_array)
            ms_wirePatternDx_capnp.append(dx_array)
            ms_wirePatternDy_capnp.append(dy_array)
            ms_wirePatternToWire_capnp.append(wirePattern_array)


            # get tilePatterns
            for tile in solution[0]:
                tile_idx = ms_tilePkeys.index(tile.tile_pkey)
                ms_tilePatterns[tile_idx].append(subgraph_idx)
        for tile_pattern in ms_tilePatterns:
            ms_tile_patterns_array = CompactArray()
            ms_tile_patterns_array.set_items(tile_pattern)
            ms_tile_patterns_capnp.append(ms_tile_patterns_array)

        ms_node_wire_in_tile_pkeys_capnp, ms_tile_pkeys_capnp = CompactArray(), CompactArray()
        ms_node_wire_in_tile_pkeys_capnp.set_items(ms_nodeWireInTilePkeys)
        ms_tile_pkeys_capnp.set_items(ms_tilePkeys)

        # write data structures that you just gathered

        ms_node_wire_in_tile_pkeys_capnp.write_to_capnp(ms_nodes_and_wires.nodeWireInTilePkeys)
        # ms_tile_pkeys_capnp.write_to_capnp(ms_nodes_and_wires.tilePkeys)

        # init subgraphs list
        subgraphs_capnp_list = ms_nodes_and_wires.init('subgraphs', len(ms_subgraphs_capnp))
        for subgraph_capnp, subgraph in zip(subgraphs_capnp_list, ms_subgraphs_capnp):
            subgraph.write_to_capnp(subgraph_capnp)
        # init dx list
        dx_capnp_list = ms_nodes_and_wires.init('wirePatternDx', len(ms_wirePatternDx_capnp))
        for dx_capnp, dx in zip(dx_capnp_list, ms_wirePatternDx_capnp):
            dx.write_to_capnp(dx_capnp)
        # init dy list
        dy_capnp_list = ms_nodes_and_wires.init('wirePatternDy', len(ms_wirePatternDy_capnp))
        for dy_capnp, dy in zip(dy_capnp_list, ms_wirePatternDy_capnp):
            dy.write_to_capnp(dy_capnp)
        # init wire_pattern list
        wire_pattern_capnp_list = ms_nodes_and_wires.init('wirePatternToWire', len(ms_wirePatternToWire_capnp))
        for wire_pattern_capnp, wire_pattern in zip(wire_pattern_capnp_list, ms_wirePatternToWire_capnp):
            wire_pattern.write_to_capnp(wire_pattern_capnp)
        # # init tilePatterns list
        # tile_patterns_capnp_list = ms_nodes_and_wires.init('tilePatterns', len(ms_tile_patterns_capnp))
        # for tile_pattern_capnp, tile_pattern in zip(tile_patterns_capnp_list, ms_tile_patterns_capnp):
        #     tile_pattern.write_to_capnp(tile_pattern_capnp)            


        tile_patterns_data = []
        tile_pattern_to_index = {}
        for idx, tile_pattern in enumerate(tile_patterns):
            tile_pattern_to_index[tile_pattern] = idx
            tile_pattern_data = CompactArray()

            # Have tile patterns put more complete subgraphs earlier than later.
            tile_pattern_data.set_items(
                sorted(tile_pattern))
            tile_patterns_data.append(tile_pattern_data)

        tile_to_tile_patterns_data = []
        for tile, tile_pattern in tile_to_tile_patterns.items():
            tile_to_tile_patterns_data.append(
                (tile.tile_pkey, tile_pattern_to_index[tile_pattern]))

        tile_to_tile_patterns = StructOfArray(
            'TileToTilePatterns', ('tile_pkey', 'tile_pattern_index'))
        tile_to_tile_patterns.set_items(sorted(tile_to_tile_patterns_data))




         # init tilePatterns list
        tile_patterns_capnp = ms_nodes_and_wires.init(
            'tilePatterns', len(tile_patterns_data))
        # write tilePatterns
        for tile_pattern_capnp, tile_pattern in zip(tile_patterns_capnp,
                                                    tile_patterns_data):
            tile_pattern.write_to_capnp(tile_pattern_capnp)

        # write tileToTilePatterns
        tile_to_tile_patterns.write_to_capnp(
            (ms_nodes_and_wires.tilePkeys, ms_nodes_and_wires.tileToTilePatterns))


        final_node_to_wires = ms_nodes_and_wires



    serialized = final_node_to_wires.to_bytes()
    if use_prints["size_on_disk"]:
        print(f'{cover_method} Size on disk: ', len(serialized))

    def printCapnp(node_to_wires):
        global use_prints
        if use_prints["printCapnp"]:
            n2w = str(node_to_wires)
            all_pattern = """(?:storage.*?= )(\[.*?\])|(nodeWireInTilePkeys|wirePatternDx|wirePatternDy|
                                wirePatternToWire|nodePatterns|tilePatterns|tilePkeys|tileToTilePatterns|subgraphs)"""
            regex_result = re.findall(all_pattern, n2w, re.DOTALL)
            for cur_result in regex_result:
                for this_result in cur_result:
                    print(this_result.replace(',', '\n'))
            print(regex_result)

    def printSubgraphNones(subgraphs, node_wire_in_tile_pkeys_array):
        global use_prints
        if use_prints["printSubgraphNones"]:
            all_set = set()
            for subgraph in subgraphs:
                ordered_list = []
                for idx, pattern_idx in enumerate(subgraph.items):
                    if pattern_idx is None:
                        pattern_idx = '-'
                    else:
                        pattern_idx = str(node_wire_in_tile_pkeys_array.items[idx])[-1]
                        ordered_list.append(pattern_idx)
                    #print(f'{pattern_idx} ',end='')
                # for starting_pkey in ordered_list:
                #     print(f'{starting_pkey} ',end='')
                ordered_tuple = tuple(ordered_list)
                all_set.add(ordered_tuple)
                print()
            print(tile_type)
            for pattern in all_set:
                for item in pattern:
                    print(item, end=' ')
                print()



        print('here')

    #nodeWireInTilePkeys	wirePatternDx	wirePatternDy	wirePatternToWire	nodePatterns	subgraphs	tilePatterns	tilePkeys tileToTilePatterns
    #printSubgraphNones(subgraphs, node_wire_in_tile_pkeys_array)
    printCapnp(final_node_to_wires)

    # with open(f'tile_json/{tile_type}.json', 'w') as fp:
    #     json.dump(all_info, fp)

    if output_dir:
        if only_pips:
            fname = '{}_node_to_pip_wires.bin'.format(tile_type)
        else:
            fname = '{}_node_to_wires.bin'.format(tile_type)

        with open(os.path.join(output_dir, fname), 'wb') as f:
            f.write(serialized)
    return len(serialized), final_node_to_wires

def write_nodes_and_wires(
        graph, required_solutions, tile_patterns, tile_to_tile_patterns,
        output_dir, tile_type, only_pips, cover_method):
    global use_prints

    if use_prints['write_to_type']:
        if only_pips:
            print(f"                        {tile_type}     Node to wires (only pips)   {cover_method}")
        else:
            print(f"                        {tile_type}     Node to wires   {cover_method}")

    if cover_method == 'max_shared':
        ms_graph_storage_schema = capnp.load('max_shared_storage.capnp')
        ms_nodes_and_wires = ms_graph_storage_schema.NodesAndWiresStorage.new_message()

        # get tilePkeys
        ms_tilePkeys = []
        for tile in graph.u:
            ms_tilePkeys.append(tile.tile_pkey)
        ms_tilePkeys = sorted(ms_tilePkeys)
        
        #get nodeWireInTilePkeys
        ms_nodeWireInTilePkeys = []
        for v in graph.v:
            ms_nodeWireInTilePkeys.append(v[0])
        ms_nodeWireInTilePkeys = sorted(list(set(ms_nodeWireInTilePkeys))) #remove duplicates and order them

        #create tilePatterns
        ms_tilePatterns = []
        ms_tile_patterns_capnp = []
        for i in range(len(ms_tilePkeys)): # create empty list of lists (one for each tile)
             ms_tilePatterns.append([])
             
        ms_subgraphs, ms_wirePatternDx, ms_wirePatternDy, ms_wirePatternToWire, ms_hasPip = [], [], [], [], []

        ms_subgraphs_capnp, ms_wirePatternDx_capnp, ms_wirePatternDy_capnp, ms_wirePatternToWire_capnp, ms_hasPip_capnp = [], [], [], [], []

        for i in range(len(required_solutions)): # create empty list of lists of subgraph, dx, dy, and wirePatternToWire (one for each subgraph)
            ms_subgraphs.append([])
            ms_wirePatternDx.append([])
            ms_wirePatternDy.append([])
            ms_wirePatternToWire.append([])
            ms_hasPip.append([])
        for subgraph_idx, solution in enumerate(required_solutions):
            for wirePattern in solution[1]:
                cur_nodeWireInTilePkey = wirePattern[0]
                for dx_dy_pkey in wirePattern[1]:
                    #ms_subgraphs[subgraph_idx].append(ms_nodeWireInTilePkeys.index(cur_nodeWireInTilePkey)) # add the nodeWireInTilePkey to the current subgraph
                    ms_subgraphs[subgraph_idx].append(cur_nodeWireInTilePkey) # add the nodeWireInTilePkey to the current subgraph
                    ms_wirePatternDx[subgraph_idx].append(dx_dy_pkey.delta_x)
                    ms_wirePatternDy[subgraph_idx].append(dx_dy_pkey.delta_y)
                    ms_wirePatternToWire[subgraph_idx].append(dx_dy_pkey.wire_in_tile_pkey)
                    ms_hasPip[subgraph_idx].append(dx_dy_pkey.has_pip_from)
            subgraph_array, dx_array, dy_array, wirePattern_array, has_pip_array = CompactArray(), CompactArray(), CompactArray(), CompactArray(), CompactArray()
            subgraph_array.set_items(ms_subgraphs[subgraph_idx])
            dx_array.set_items(ms_wirePatternDx[subgraph_idx])
            dy_array.set_items(ms_wirePatternDy[subgraph_idx])
            wirePattern_array.set_items(ms_wirePatternToWire[subgraph_idx])
            has_pip_array.set_items(ms_hasPip[subgraph_idx])

            ms_subgraphs_capnp.append(subgraph_array)
            ms_wirePatternDx_capnp.append(dx_array)
            ms_wirePatternDy_capnp.append(dy_array)
            ms_wirePatternToWire_capnp.append(wirePattern_array)
            ms_hasPip_capnp.append(has_pip_array)


            # get tilePatterns
            for tile in solution[0]:
                tile_idx = ms_tilePkeys.index(tile.tile_pkey)
                ms_tilePatterns[tile_idx].append(subgraph_idx)
        for tile_pattern in ms_tilePatterns:
            ms_tile_patterns_array = CompactArray()
            ms_tile_patterns_array.set_items(tile_pattern)
            ms_tile_patterns_capnp.append(ms_tile_patterns_array)

        ms_node_wire_in_tile_pkeys_capnp, ms_tile_pkeys_capnp = CompactArray(), CompactArray()
        ms_node_wire_in_tile_pkeys_capnp.set_items(ms_nodeWireInTilePkeys)
        ms_tile_pkeys_capnp.set_items(ms_tilePkeys)

        # write data structures that you just gathered

        ms_node_wire_in_tile_pkeys_capnp.write_to_capnp(ms_nodes_and_wires.nodeWireInTilePkeys)
        # ms_tile_pkeys_capnp.write_to_capnp(ms_nodes_and_wires.tilePkeys)

        # init subgraphs list
        subgraphs_capnp_list = ms_nodes_and_wires.init('subgraphs', len(ms_subgraphs_capnp))
        for subgraph_capnp, subgraph in zip(subgraphs_capnp_list, ms_subgraphs_capnp):
            subgraph.write_to_capnp(subgraph_capnp)
        # init dx list
        dx_capnp_list = ms_nodes_and_wires.init('wirePatternDx', len(ms_wirePatternDx_capnp))
        for dx_capnp, dx in zip(dx_capnp_list, ms_wirePatternDx_capnp):
            dx.write_to_capnp(dx_capnp)
        # init dy list
        dy_capnp_list = ms_nodes_and_wires.init('wirePatternDy', len(ms_wirePatternDy_capnp))
        for dy_capnp, dy in zip(dy_capnp_list, ms_wirePatternDy_capnp):
            dy.write_to_capnp(dy_capnp)
        # init wire_pattern list
        wire_pattern_capnp_list = ms_nodes_and_wires.init('wirePatternToWire', len(ms_wirePatternToWire_capnp))
        for wire_pattern_capnp, wire_pattern in zip(wire_pattern_capnp_list, ms_wirePatternToWire_capnp):
            wire_pattern.write_to_capnp(wire_pattern_capnp)
        # init hasPip list
        has_pip_capnp_list = ms_nodes_and_wires.init('hasPip', len(ms_hasPip_capnp))
        for has_pip_capnp, has_pip in zip(has_pip_capnp_list, ms_hasPip_capnp):
            has_pip.write_to_capnp(has_pip_capnp)

        # # init tilePatterns list
        # tile_patterns_capnp_list = ms_nodes_and_wires.init('tilePatterns', len(ms_tile_patterns_capnp))
        # for tile_pattern_capnp, tile_pattern in zip(tile_patterns_capnp_list, ms_tile_patterns_capnp):
        #     tile_pattern.write_to_capnp(tile_pattern_capnp)            


        tile_patterns_data = []
        tile_pattern_to_index = {}
        for idx, tile_pattern in enumerate(tile_patterns):
            tile_pattern_to_index[tile_pattern] = idx
            tile_pattern_data = CompactArray()

            # Have tile patterns put more complete subgraphs earlier than later.
            tile_pattern_data.set_items(
                sorted(tile_pattern))
            tile_patterns_data.append(tile_pattern_data)

        tile_to_tile_patterns_data = []
        for tile, tile_pattern in tile_to_tile_patterns.items():
            tile_to_tile_patterns_data.append(
                (tile.tile_pkey, tile_pattern_to_index[tile_pattern]))

        tile_to_tile_patterns = StructOfArray(
            'TileToTilePatterns', ('tile_pkey', 'tile_pattern_index'))
        tile_to_tile_patterns.set_items(sorted(tile_to_tile_patterns_data))




         # init tilePatterns list
        tile_patterns_capnp = ms_nodes_and_wires.init(
            'tilePatterns', len(tile_patterns_data))
        # write tilePatterns
        for tile_pattern_capnp, tile_pattern in zip(tile_patterns_capnp,
                                                    tile_patterns_data):
            tile_pattern.write_to_capnp(tile_pattern_capnp)

        # write tileToTilePatterns
        tile_to_tile_patterns.write_to_capnp(
            (ms_nodes_and_wires.tilePkeys, ms_nodes_and_wires.tileToTilePatterns))


        final_node_to_wires = ms_nodes_and_wires



    serialized = final_node_to_wires.to_bytes()
    if use_prints["size_on_disk"]:
        print(f'{cover_method} Size on disk: ', len(serialized))

    def printCapnp(node_to_wires):
        global use_prints
        if use_prints["printCapnp"]:
            n2w = str(node_to_wires)
            all_pattern = """(?:storage.*?= )(\[.*?\])|(nodeWireInTilePkeys|wirePatternDx|wirePatternDy|
                                wirePatternToWire|nodePatterns|tilePatterns|tilePkeys|tileToTilePatterns|subgraphs)"""
            regex_result = re.findall(all_pattern, n2w, re.DOTALL)
            for cur_result in regex_result:
                for this_result in cur_result:
                    print(this_result.replace(',', '\n'))
            print(regex_result)

    def printSubgraphNones(subgraphs, node_wire_in_tile_pkeys_array):
        global use_prints
        if use_prints["printSubgraphNones"]:
            all_set = set()
            for subgraph in subgraphs:
                ordered_list = []
                for idx, pattern_idx in enumerate(subgraph.items):
                    if pattern_idx is None:
                        pattern_idx = '-'
                    else:
                        pattern_idx = str(node_wire_in_tile_pkeys_array.items[idx])[-1]
                        ordered_list.append(pattern_idx)
                    #print(f'{pattern_idx} ',end='')
                # for starting_pkey in ordered_list:
                #     print(f'{starting_pkey} ',end='')
                ordered_tuple = tuple(ordered_list)
                all_set.add(ordered_tuple)
                print()
            print(tile_type)
            for pattern in all_set:
                for item in pattern:
                    print(item, end=' ')
                print()



        print('here')

    #nodeWireInTilePkeys	wirePatternDx	wirePatternDy	wirePatternToWire	nodePatterns	subgraphs	tilePatterns	tilePkeys tileToTilePatterns
    #printSubgraphNones(subgraphs, node_wire_in_tile_pkeys_array)
    printCapnp(final_node_to_wires)

    # with open(f'tile_json/{tile_type}.json', 'w') as fp:
    #     json.dump(all_info, fp)

    if output_dir:
        if only_pips:
            fname = '{}_nodes_and_pip_wires.bin'.format(tile_type)
        else:
            fname = '{}_nodes_and_wires.bin'.format(tile_type)

        with open(os.path.join(output_dir, fname), 'wb') as f:
            f.write(serialized)

    return len(serialized), final_node_to_wires


def find_duplicate_pairs(solutions):
    # Find number of duplicate sets of u->v pairs (ie Tile -> Pattern)
    print("finding duplicates")
    subgraph_vs = []
    u_to_v_pairs = []
    subgraph_v_duplicates = 0
    u_to_v_duplicates = 0
    global use_progressbar
    for subgraph_num, subgraph in enumerate(solutions):
        iterator = progressbar.progressbar(enumerate(subgraph[0])) if use_progressbar else enumerate(subgraph[0])
        for tile_num, tile in iterator:
            tile_pkey = tile.tile_pkey #needed
            for pattern in subgraph[1]:
                starting_pkey = pattern[0]
                u_to_v = str(tile_pkey) + " " + str(pattern[1])
                v = str(pattern[1])
                if u_to_v not in u_to_v_pairs:
                    u_to_v_pairs.append(u_to_v)
                else:
                    u_to_v_duplicates += 1
                if tile_num == 0: # only check the vs if you're going through the loop for the first time
                    if v not in subgraph_vs:
                        subgraph_vs.append(v)
                    else:
                        subgraph_v_duplicates += 1
                

    duplicates = f"    Found {subgraph_v_duplicates} subgraph_v duplicates\n"
    duplicates += f"    Found {u_to_v_duplicates} u_to_v duplicates\n"
    print(duplicates)

    return duplicates

def generate_max_shared_subgraphs(graph):
    global use_prints
    total_number_of_vs = len(graph.u_to_v[0])
    total_number_of_us = len(graph.u_to_v)
    all_needed_u_combinations = {}
    possible_u_combinations = f"2^{total_number_of_us}"

    tile_and_tile_solutions = {}

    # Find the total number of required subgraphs (Maybe use pandas here later)
    all_tiles = {}
    for v_idx in range(total_number_of_vs-1): # for every column
        cur_u_combination = bitarray()
        cur_tiles_in_subgraph = [] # this will represent the u's in the subgraph
        # cur_patterns_in_subgraph = {} # this will represent the v's in the subgraph
        for u_idx, u in enumerate(graph.u_to_v): # for every row (every row is a tile)
            cur_u_combination.append(u[v_idx])
            if u[v_idx]:
                cur_tiles_in_subgraph.append(graph.u[u_idx])
            if graph.u[u_idx] not in all_tiles:
                all_tiles[graph.u[u_idx]] = []
        if str(cur_u_combination) not in all_needed_u_combinations: # first time seeing this set of tiles, so add it
            all_needed_u_combinations[str(cur_u_combination)] = {"u": cur_tiles_in_subgraph, "v": [graph.v[v_idx]]}
        else:
            all_needed_u_combinations[str(cur_u_combination)]["v"].append(graph.v[v_idx])
    


    required_solutions = []
    for tile_set in all_needed_u_combinations: # format all_needed_u_combinations in a required_solutions format
        u = frozenset(all_needed_u_combinations[tile_set]['u'])
        v = frozenset(all_needed_u_combinations[tile_set]['v'])
        required_solutions.append((u, v))

    for solution_idx, solution in enumerate(required_solutions):
        for tile in all_tiles:
            if tile in solution[0]:
                all_tiles[tile].append(solution_idx)


    if use_prints["needed_combinations"]:
        max_shared = f"""        There are {len(all_needed_u_combinations)} needed u combinations out of a possible {possible_u_combinations} from {total_number_of_us} u's\n"""
    #max_shared += f"        They are: {str(all_needed_u_combinations)}"

        print(max_shared)

    return required_solutions, all_tiles








def reduce_graph(args, all_edges, graph, tile_type):
    global use_ms
    global use_gs
    global use_prints
>>>>>>> 7bf2be5c... All changed for max shared algorithm. The code is not yet complete, but this is just a work in progress.
    density = graph.density()
    beta = .5
    P = (0.6 - 0.8 * beta) * math.exp((4 + 3 * beta) * density)
    N = 0.01 * len(graph.u) * len(graph.v)

    if args.wire_to_node:
        tile_wire_ids = set()
        wire_nodes = set()
        dxdys = set()
        max_dxdy = 0
        for pattern in graph.v:
            tile_wire_ids.add(pattern.node_wire_in_tile_pkey)
            wire_nodes.add(pattern.wire_in_tile_pkey)
            dxdys.add((pattern.delta_x, pattern.delta_y))
            max_dxdy = max(max_dxdy, abs(pattern.delta_x))
            max_dxdy = max(max_dxdy, abs(pattern.delta_y))

        print('Wire nodes {}'.format(len(wire_nodes)))
        print('Unique node wire in tile pkey {}'.format(len(tile_wire_ids)))
        print('Unique pattern {}'.format(len(graph.v)))
        print('Unique dx dy {}'.format(len(dxdys)))
        print('Unique dx dy dist {}'.format(max_dxdy))
    elif args.node_to_wires or args.nodes_and_wires:
        tile_wire_ids = set()
        node_wires = set()
        patterns = set()
        dxdys = set()
        max_dxdy = 0
        max_patterns_to_node = 0

        node_to_wires_to_count = {}

        for node_wire_in_tile_pkey, node_to_wires in graph.v:
            node_wires.add(node_wire_in_tile_pkey)

            if node_to_wires not in node_to_wires_to_count:
                node_to_wires_to_count[node_to_wires] = len(node_to_wires)

            max_patterns_to_node = max(max_patterns_to_node, len(node_to_wires))
            for pattern in node_to_wires:
                patterns.add(pattern)
                tile_wire_ids.add(pattern.wire_in_tile_pkey)
                dxdys.add((pattern.delta_x, pattern.delta_y))
                max_dxdy = max(max_dxdy, abs(pattern.delta_x))
                max_dxdy = max(max_dxdy, abs(pattern.delta_y))

        pattern_count = 0
        max_node_to_wires = 0
        for num_patterns in node_to_wires_to_count.values():
            pattern_count += num_patterns
            max_node_to_wires = max(max_node_to_wires, num_patterns)

        print_and_json('Node wires: {}'.format(len(node_wires)))
        print_and_json('Max number of patterns: {}'.format(max_node_to_wires))
        print_and_json('Minimum number of pattern storage: {}'.format(pattern_count))
        print_and_json('Unique wire in tile pkey: {}'.format(len(tile_wire_ids)))
        print_and_json('Unique node_to_wires: {}'.format(len(graph.v)))
        print_and_json('Unique patterns: {}'.format(len(patterns)))
        print_and_json('Unique dx dy: {}'.format(len(dxdys)))
        print_and_json('Unique dx dy dist: {}'.format(max_dxdy))

    else:
        assert False

    if use_prints["density"]:
        print(
            'density = {}, beta = {}, P = {}, N = {}'.format(density, beta, P, N))

    P = math.ceil(P)
    N = math.ceil(N)

    required_solutions = {}
    if use_gs:
        found_solutions_time = time.time()
        found_solutions, remaining_edges = find_bsc_par(
            num_workers=40, batch_size=100, graph=graph, N=N, P=P)
        found_solutions_time = time.time() - found_solutions_time
        assert len(remaining_edges) == 0
        print('Found {} possible complete subgraphs'.format(len(found_solutions)))

    
        #printBicliques(found_solutions)
        greedy_set_time = time.time()
        required_solutions = greedy_set_cover_with_complete_bipartite_subgraphs(
            all_edges, found_solutions)
        print(f"gs took {found_solutions_time}s to find subgraphs and {time.time()-greedy_set_time}s to choose them")
        required_solutions.sort()

        print(
            '{} complete subgraphs required for solution'.format(
                len(required_solutions)))
        solution_to_idx = {}
        for idx, solution in enumerate(required_solutions):
            solution_to_idx[solution] = idx

    ms_required_solutions = {}

    if use_ms:
        start_time = time.time()
        ms_required_solutions, tile_and_tile_solutions = generate_max_shared_subgraphs(graph) # ESR added this for the max_shared_subgraphs
        if use_prints["ms_runtime"]:
            print(f"Max Shared took {time.time() - start_time} seconds to run")
        #ms_required_solutions.sort()

        ms_solution_to_idx = {}
        for idx, solution in enumerate(ms_required_solutions):
            ms_solution_to_idx[solution] = idx

    def get_tile_edges():
        for tile in graph.u:
            edges = set()
            for vj_idx, is_set in enumerate(graph.get_row(tile)):
                if is_set:
                    pattern = graph.v[vj_idx]
                    edges.add((tile, pattern))

            yield tile, edges

    tile_patterns = set()
    tile_to_tile_patterns = {}

    ms_tile_patterns = set()
    ms_tile_to_tile_patterns = {}

    global use_progressbar
    if use_gs:
        iterator = progressbar.progressbar(
                greed_set_cover_par(num_workers=40,
                                    required_solutions=required_solutions,
                                    edges_iter=get_tile_edges())) if use_progressbar else greed_set_cover_par(num_workers=40,
                                    required_solutions=required_solutions,
                                    edges_iter=get_tile_edges())
        for tile, solutions_for_tile in iterator:
            tile_pattern = set()
            for solution in solutions_for_tile:
                tile_pattern.add(solution_to_idx[solution])

            tile_pattern = frozenset(tile_pattern)
            tile_to_tile_patterns[tile] = tile_pattern
            tile_patterns.add(tile_pattern)

    if use_ms:
        for tile in tile_and_tile_solutions:
            solutions_for_tile = tile_and_tile_solutions[tile]
            tile_pattern = set()
            for solution in solutions_for_tile:
                tile_pattern.add(solution)
                #tile_pattern.add(solution_to_idx[solution])

            tile_pattern = frozenset(tile_pattern)
            ms_tile_to_tile_patterns[tile] = tile_pattern
            ms_tile_patterns.add(tile_pattern)


    number_of_tile_pattern_elements = 0
    for tile_pattern in tile_patterns:
        number_of_tile_pattern_elements += len(tile_pattern)

<<<<<<< HEAD
    print('Have {} tile patterns'.format(len(tile_patterns)))
    print(
        'Max {} patterns'.format(
            max(len(patterns) for patterns in tile_to_tile_patterns.values())))
    print('Number of tile pattern elements: {}'.format(number_of_tile_pattern_elements))
=======
    # print('Have {} tile patterns'.format(len(tile_patterns)))
    # print(
    #     'Max {} patterns'.format(
    #         max(len(patterns) for patterns in tile_to_tile_patterns.values())))
    # print(
    #     'Number of tile pattern elements: {}'.format(
    #         number_of_tile_pattern_elements))

    #duplicates = find_duplicate_pairs(required_solutions)

    # write_this = f"{tile_type}:\n{duplicates}{max_shared} \n\n"

    # f = open("max_shared_subgraphs.txt", "a")
    # f.write(write_this)
    # f.close()



    return required_solutions, tile_patterns, tile_to_tile_patterns, ms_required_solutions, ms_tile_patterns, ms_tile_to_tile_patterns


def printBicliques(found_solutions):
    biclique_string = ''
    biclique_string += "There are {} bicliques:\n".format(len(found_solutions))
    for s in found_solutions:
        assert len(s) == 2
        biclique_string += "Bicliques:    s is one biclique and is a tuple (setOfTiles, setOfNodeToWire)\n"
        biclique_string += "         Tiles:\n"
        for t in s[0]:
            biclique_string += "               {}\n".format(t)
        biclique_string += "         NodeToWires:\n"
        for ntw in s[1]:
            biclique_string += "               {}\n".format(ntw)
    print_and_json(f'Bicliques:{biclique_string}')
    if len(found_solutions) > 10:
        print(biclique_string)
    
def printSubgraphs(required_solutions):
    for subgraph in required_solutions:
        print('Tiles:', end='')
        for tile in subgraph[0]:
            print(tile.tile_pkey, end=',')
        print(f' ({len(subgraph[1])} patterns)')
        for v in subgraph[1]:
            print(v,)
        print('')


def printGraph(graph, msg):
    print("\nPrinting graph {}:".format(msg))
    print("The u's are:")
    for u in graph.u:
        print(f"    {u}")
    print("The ui_to_idx's are:")
    for idx, ux in enumerate(graph.ui_to_idx):
        print(f"    {idx} {ux}")
    print("The v's are:")
    print('vkey wire_in_tile_pkey  deltax  deltay')
    for v in graph.v:
        print(f"{v[0]}", end='')
        for cur_set in v[1]:
            print(f"   ({cur_set.wire_in_tile_pkey}, {cur_set.delta_x}, {cur_set.delta_y})", end='')
        print('')
    print("The vj_to_idx's are:")
    for idx, vx in enumerate(graph.vj_to_idx):
        print(f"    {idx} {vx}")
    print("The u_to_v's are:")
    for idx, u2v in enumerate(graph.u_to_v):
        print(f"    {idx} {u2v}")
    print("The v_to_u's are:")
    for idx, v2u in enumerate(graph.v_to_u):
        print(f"    {idx} {v2u}")
    print("\n")

def main():

    global use_ms
    global use_gs
    global use_prints
    multiprocessing.set_start_method('spawn')

    

    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    parser.add_argument('--tile', required=True)
    parser.add_argument('--wire_to_node', action='store_true')
    parser.add_argument('--node_to_wires', action='store_true')
    parser.add_argument('--nodes_and_wires', action='store_true')
    parser.add_argument('--output_dir')
    parser.add_argument('--only_pips', action='store_true')
    parser.add_argument('--legacy', action='store_true')

    args = parser.parse_args()

    if args.node_to_wires:
        if args.only_pips:
            print("Node to wires only pips...")
        else:
            print("Node to wires...")
    elif args.wire_to_node:
        print("Wire to node...")
    elif args.nodes_and_wires:
        print("Nodes and wires...")

    if args.wire_to_node and args.node_to_wires:
        parser.error('Cannot supply both --wire_to_node and --node_to_wires')
    elif not args.wire_to_node and not args.node_to_wires and not args.nodes_and_wires:
        parser.error('Must supply --wire_to_node or --node_to_wires')

    def check_file_existence(cur_file):
        return
        if os.path.isfile(cur_file):
            print()
            print(f"***File {cur_file} already exists***")
            exit()

    cur_file = os.path.join(args.output_dir,f'{args.tile}')
    if args.wire_to_node:
        check_file_existence(cur_file+'_wire_to_nodes.bin')
        graph = get_wire_to_node_graph(args.database, args.tile)
    elif args.node_to_wires:
        ending = '_node_to_pip_wires.bin' if args.only_pips else '_node_to_wires.bin'
        check_file_existence(cur_file+ending)
        graph = get_node_to_wires_graph(
            args.database, args.tile, args.only_pips)
    elif args.nodes_and_wires:
        graph = get_node_to_wires_graph(
            args.database, args.tile, args.only_pips)
    else:
        assert False

    if use_prints["processing_build"]:
        print('Processing {} : {}'.format(args.database, args.tile))

    all_edges = set(graph.frozen_edges)
    gc.collect()

    if len(all_edges) != 0:
        required_solutions, tile_patterns, tile_to_tile_patterns, ms_required_solutions, ms_tile_patterns, ms_tile_to_tile_patterns = reduce_graph(
            args, all_edges, graph, args.tile)
    else:
        required_solutions = set()
        tile_patterns = set()
        tile_to_tile_patterns = {}
        ms_required_solutions = set()  
        ms_tile_patterns = set()
        ms_tile_to_tile_patterns = {}

    if args.wire_to_node:
        if use_gs:
            gs_size, gs_wire_to_nodes = write_wire_to_node(
                graph, required_solutions, tile_patterns, tile_to_tile_patterns,
                args.output_dir, args.tile, 'greedy_set')
        if use_ms:
            ms_size, ms_wire_to_nodes = write_wire_to_node(
                graph, ms_required_solutions, ms_tile_patterns, ms_tile_to_tile_patterns,
                args.output_dir, args.tile, 'max_shared')
            

    if args.node_to_wires:
        if use_gs:
            gs_size, gs_node_to_wires = write_node_to_wires( 
                graph, required_solutions, tile_patterns, tile_to_tile_patterns,
                args.output_dir, args.tile, args.only_pips, 'greedy_set')
        if use_ms: # if you want to try the max_shared algorithm
            ms_size, ms_nodes_and_wires = write_node_to_wires( 
                graph, ms_required_solutions, ms_tile_patterns, ms_tile_to_tile_patterns, args.output_dir, args.tile, args.only_pips, 'max_shared')
    
    if args.nodes_and_wires:
        if use_ms: # if you want to try the max_shared algorithm
            ms_size, ms_nodes_and_wires = write_nodes_and_wires( 
                graph, ms_required_solutions, ms_tile_patterns, ms_tile_to_tile_patterns, args.output_dir, args.tile, args.only_pips, 'max_shared')
    
    if use_ms:
        print(f"ms_size: {ms_size}")
    if use_gs:
        print(f"gs_size: {gs_size}")
    if use_ms and use_gs:            
        size_diff = gs_size - ms_size
        
        ms_required_solutions_info = []
        for cur_solution in ms_required_solutions:
            ms_required_solutions_info.append((len(cur_solution[0]), len(cur_solution[1])))
        gs_required_solutions_info = []
        for cur_solution in required_solutions:
            gs_required_solutions_info.append((len(cur_solution[0]), len(cur_solution[1])))

        #print(f'ms: {len(ms_required_solutions)} subgraphs. (tiles,patterns) {ms_required_solutions_info}')
        #print(f'gs: {len(required_solutions)} subgraphs. (tiles,patterns) {gs_required_solutions_info}')
        # print('ms:')
        # printSubgraphs(ms_required_solutions)
        # print('gs:')
        # printSubgraphs(required_solutions)

        print(f"gs_size: {gs_size}, ms_size: {ms_size}")

        if size_diff > 0:
            print(f'{args.tile:20s} max_shared size better by {size_diff:8d} ({100*size_diff/gs_size:.2f}%)')
        if size_diff < 0:
            print(f'{args.tile:20s} greedy_set size better by {abs(size_diff):8d} ({100*size_diff/ms_size:2.2f}%)')
        if size_diff == 0:
            print(f'{args.tile} Sizes were the same')


"""


"""

>>>>>>> 7bf2be5c... All changed for max shared algorithm. The code is not yet complete, but this is just a work in progress.


if __name__ == "__main__":
    main()
