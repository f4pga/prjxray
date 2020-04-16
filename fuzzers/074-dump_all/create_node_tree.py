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
import datetime
import progressbar
import os.path
import prjxray.lib
import pickle
import collections
import json


def build_node_index(fname):
    node_index = {}
    with open(fname, 'rb') as f:
        f.seek(0, 2)
        bytes = f.tell()
        f.seek(0, 0)
        with progressbar.ProgressBar(max_value=bytes) as bar:
            end_of_line = 0
            for l in f:
                parts = l.decode('utf8').split(' ')
                pip, node = parts[0:2]

                if node not in node_index:
                    node_index[node] = []

                node_index[node].append(end_of_line)
                end_of_line = f.tell()
                bar.update(end_of_line)

    return node_index


def read_node(expected_node, wire_file, node_index):
    with open(wire_file, 'rb') as f:
        for index in node_index:
            f.seek(index, 0)

            parts = f.readline().decode('utf8').strip().split(' ')

            pip, node = parts[0:2]
            wires = parts[2:]

            assert node == expected_node, repr((node, expected_node, index))

            yield wires


def generate_edges(graph, root, graph_nodes):
    """ Starting from root, generate an edge in dir and insert into graph.

  If the tree forks, simply insert a joins to indicate the split.

  """
    edge = [root]
    prev_root = None

    while True:
        outbound_edges = graph_nodes[root]
        outbound_edges -= set((prev_root, ))
        if len(outbound_edges) > 1:
            graph['edges'].append(edge)
            if root not in graph['joins']:
                graph['joins'][root] = set()
            graph['joins'][root] |= outbound_edges

            for element in graph_nodes[root]:
                if element not in graph['joins']:
                    graph['joins'][element] = set()
                graph['joins'][element].add(root)

            break
        else:
            if len(outbound_edges) == 0:
                graph['edges'].append(edge)
                break

            next_root = tuple(outbound_edges)[0]
            edge.append(next_root)
            prev_root, root = root, next_root


def create_ordered_wires_for_node(node, wires_in_node, downhill, uphill):
    if len(wires_in_node) <= 2:
        return {'edges': [wires_in_node], 'joins': {}}

    downhill = set(tuple(l) for l in downhill)
    uphill = set(tuple(l) for l in uphill)

    roots = set()
    all_wires = set()

    for wire in downhill:
        if len(wire) > 0:
            roots |= set((wire[0], wire[-1]))
            all_wires |= set(wire)

    for wire in uphill:
        if len(wire) > 0:
            roots |= set((wire[0], wire[-1]))
            all_wires |= set(wire)

    assert len(wires_in_node) >= len(all_wires), (
        len(wires_in_node), len(all_wires))

    if len(all_wires) <= 2:
        return {'edges': tuple(all_wires), 'joins': {}}

    graph_nodes = dict((wire, set()) for wire in all_wires)

    for wire in all_wires:
        for down in downhill:
            try:
                idx = down.index(wire)
                if idx + 1 < len(down):
                    graph_nodes[wire].add(down[idx + 1])
                if idx - 1 >= 0:
                    graph_nodes[wire].add(down[idx - 1])
            except ValueError:
                continue

        for up in uphill:
            try:
                idx = up.index(wire)
                if idx + 1 < len(up):
                    graph_nodes[wire].add(up[idx + 1])
                if idx - 1 >= 0:
                    graph_nodes[wire].add(up[idx - 1])
            except ValueError:
                continue

    graph = {'edges': [], 'joins': {}}

    while len(roots) > 0:
        root = roots.pop()

        if len(graph_nodes[root]) > 0:
            generate_edges(graph, root, graph_nodes)

    # Dedup identical edges.
    final_edges = set()

    for edge in graph['edges']:
        edge1 = tuple(edge)
        edge2 = tuple(edge[::-1])

        if edge1 > edge2:
            final_edges.add((edge2, edge1))
        else:
            final_edges.add((edge1, edge2))

    edges = [edge[0] for edge in final_edges]

    element_index = {}
    for edge in edges:
        for idx, element in enumerate(edge):
            if element not in element_index:
                element_index[element] = []
            element_index[element].append((idx, edge))

    new_edges = []
    for edge in edges:
        starts = element_index[edge[0]]
        ends = element_index[edge[-1]]

        found_any = False
        for start in starts:
            start_idx, other_edge = start
            if other_edge is edge:
                continue

            for end in ends:
                if other_edge is not end[1]:
                    continue

                found_any = True
                end_idx, _ = end
                # check if the interior elements are the same.
                if start_idx > end_idx:
                    step = -1
                else:
                    step = 1

                other_edge_slice = slice(
                    start_idx, end_idx + step if end_idx + step >= 0 else None,
                    step)
                if edge != other_edge[other_edge_slice]:
                    new_edges.append(edge)

        if not found_any:
            new_edges.append(edge)

    output = {
        'edges':
        new_edges,
        'joins':
        dict((key, tuple(value)) for key, value in graph['joins'].items()),
        'wires':
        wires_in_node,
    }

    all_wires_in_output = set()
    for edge in output['edges']:
        all_wires_in_output |= set(edge)

    for element in output['joins']:
        all_wires_in_output.add(element)

    return output


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--dump_all_root_dir', required=True)
    parser.add_argument('--ordered_wires_root_dir', required=True)
    parser.add_argument('--output_dir', required=True)

    args = parser.parse_args()

    downhill_wires = os.path.join(
        args.ordered_wires_root_dir, 'downhill_wires.txt')
    uphill_wires = os.path.join(
        args.ordered_wires_root_dir, 'uphill_wires.txt')

    assert os.path.exists(downhill_wires)
    assert os.path.exists(uphill_wires)

    print('{} Reading root.csv'.format(datetime.datetime.now()))
    tiles, nodes = prjxray.lib.read_root_csv(args.dump_all_root_dir)

    print('{} Loading node<->wire mapping'.format(datetime.datetime.now()))
    node_lookup = prjxray.lib.NodeLookup()
    node_lookup_file = os.path.join(args.output_dir, 'nodes.pickle')
    if os.path.exists(node_lookup_file):
        node_lookup.load_from_file(node_lookup_file)
    else:
        node_lookup.load_from_root_csv(nodes)
        node_lookup.save_to_file(node_lookup_file)

    wire_index_file = os.path.join(args.output_dir, 'wire_index.pickle')
    if os.path.exists(wire_index_file):
        print('{} Reading wire<->node index'.format(datetime.datetime.now()))
        with open(wire_index_file, 'rb') as f:
            wire_index = pickle.load(f)

        downhill_wire_node_index = wire_index['downhill']
        uphill_wire_node_index = wire_index['uphill']
    else:
        print('{} Creating wire<->node index'.format(datetime.datetime.now()))
        downhill_wire_node_index = build_node_index(downhill_wires)
        uphill_wire_node_index = build_node_index(uphill_wires)

        with open(wire_index_file, 'wb') as f:
            pickle.dump(
                {
                    'downhill': downhill_wire_node_index,
                    'uphill': uphill_wire_node_index,
                }, f)

    print('{} Creating node tree'.format(datetime.datetime.now()))
    nodes = collections.OrderedDict()
    for node in progressbar.progressbar(sorted(node_lookup.nodes)):
        nodes[node] = create_ordered_wires_for_node(
            node, tuple(wire['wire'] for wire in node_lookup.nodes[node]),
            tuple(
                read_node(
                    node, downhill_wires, downhill_wire_node_index[node]
                    if node in downhill_wire_node_index else [])),
            tuple(
                read_node(
                    node, uphill_wires, uphill_wire_node_index[node]
                    if node in uphill_wire_node_index else [])))

    print('{} Writing node tree'.format(datetime.datetime.now()))
    with open(os.path.join(args.output_dir, 'node_tree.json'), 'w') as f:
        json.dump(nodes, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
