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
from collections import namedtuple
import progressbar
import capnp
import capnp.lib.capnp
capnp.remove_import_hook()
import math
from distributed_bsc import BipartiteAdjacencyMatrix, find_bsc_par, \
        greedy_set_cover_with_complete_bipartite_subgraphs, \
        greed_set_cover_par
import gc
import multiprocessing

from prjxray.node_lookup import NodeLookup

Tile = namedtuple('Tile', 'tile_pkey')
WireToNode = namedtuple(
    'WireToNode', 'wire_in_tile_pkey delta_x delta_y node_wire_in_tile_pkey')
NodeToWire = namedtuple('NodeToWire', 'wire_in_tile_pkey delta_x delta_y')


def get_graph(database, tile):
    lookup = NodeLookup(database=database)
    cur = lookup.conn.cursor()
    cur2 = lookup.conn.cursor()
    cur3 = lookup.conn.cursor()

    all_tiles = set()
    all_wire_to_nodes = set()

    graph = BipartiteAdjacencyMatrix()

    cur.execute("SELECT pkey FROM tile_type WHERE name = ?;", (tile, ))
    tile_type_pkey = cur.fetchone()[0]

    for tile_pkey, tile_type_pkey, tile_name, tile_x, tile_y in progressbar.progressbar(
            cur.execute(
                "SELECT pkey, tile_type_pkey, name, x, y FROM tile WHERE tile_type_pkey = ?;",
                (tile_type_pkey, ))):
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

            pattern = WireToNode(
                wire_in_tile_pkey=wire_in_tile_pkey,
                delta_x=node_tile_x - tile_x,
                delta_y=node_tile_y - tile_y,
                node_wire_in_tile_pkey=node_wire_in_tile_pkey)

            if pattern not in all_wire_to_nodes:
                all_wire_to_nodes.add(pattern)
                graph.add_v(pattern)

            graph.add_edge(tile, pattern)

    graph.build()

    return graph


def main():
    multiprocessing.set_start_method('spawn')

    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    parser.add_argument('--tile', required=True)

    args = parser.parse_args()

    graph = get_graph(args.database, args.tile)
    all_edges = set(graph.frozen_edges)
    gc.collect()

    density = graph.density()
    beta = .5
    P = (0.6 - 0.8 * beta) * math.exp((4 + 3 * beta) * density)
    N = 0.01 * len(graph.u) * len(graph.v)

    tile_wire_ids = set()
    dxdys = set()
    max_dxdy = 0
    for pattern in graph.v:
        tile_wire_ids.add(pattern.node_wire_in_tile_pkey)
        dxdys.add((pattern.delta_x, pattern.delta_y))
        max_dxdy = max(max_dxdy, abs(pattern.delta_x))
        max_dxdy = max(max_dxdy, abs(pattern.delta_y))

    print('Unique node wire in tile pkey {}'.format(len(tile_wire_ids)))
    print('Unique pattern {}'.format(len(graph.v)))
    print('Unique dx dy {}'.format(len(dxdys)))
    print('Unique dx dy dist {}'.format(max_dxdy))
    print(
        'density = {}, beta = {}, P = {}, N = {}'.format(density, beta, P, N))

    P = math.ceil(P)
    N = math.ceil(N)

    found_solutions, remaining_edges = find_bsc_par(
        num_workers=40, batch_size=100, graph=graph, N=N, P=P)
    assert len(remaining_edges) == 0
    print('Found {} possible complete subgraphs'.format(len(found_solutions)))

    required_solutions = greedy_set_cover_with_complete_bipartite_subgraphs(
        all_edges, found_solutions)
    print(
        '{} complete subgraphs required for solution'.format(
            len(required_solutions)))

    required_solutions.sort()

    solution_to_idx = {}
    for idx, solution in enumerate(required_solutions):
        solution_to_idx[solution] = idx

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

    for tile, solutions_for_tile in progressbar.progressbar(
            greed_set_cover_par(num_workers=40,
                                required_solutions=required_solutions,
                                edges_iter=get_tile_edges())):
        tile_pattern = set()
        for solution in solutions_for_tile:
            tile_pattern.add(solution_to_idx[solution])

        tile_pattern = frozenset(tile_pattern)
        tile_to_tile_patterns[tile] = tile_pattern
        tile_patterns.add(tile_pattern)

    print('Have {} tile patterns'.format(len(tile_patterns)))
    print(
        'Max {} patterns'.format(
            max(len(patterns) for patterns in tile_to_tile_patterns.values())))

    #for tile, pattern in tile_to_tile_patterns.items():
    #    print(tile, pattern)


if __name__ == "__main__":
    main()
