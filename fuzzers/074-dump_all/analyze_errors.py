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
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument('--error_nodes', default='output/error_nodes.json')
    parser.add_argument('--output_ignore_list', action='store_true')

    args = parser.parse_args()

    with open(args.error_nodes) as f:
        flat_error_nodes = json.load(f)

    error_nodes = {}
    for node, raw_node, generated_nodes in flat_error_nodes:
        if node not in error_nodes:
            error_nodes[node] = {
                'raw_node': set(raw_node),
                'generated_nodes': set(),
            }

        assert error_nodes[node]['raw_node'] == set(raw_node)
        error_nodes[node]['generated_nodes'].add(
            tuple(sorted(generated_nodes)))

    ignored_wires = set()

    for node, error in error_nodes.items():
        combined_generated_nodes = set()
        for generated_node in error['generated_nodes']:
            combined_generated_nodes |= set(generated_node)

        # Make sure there are not extra wires in nodes.
        assert error['raw_node'] == combined_generated_nodes, (node, error)

        good_node = max(error['generated_nodes'], key=lambda x: len(x))
        bad_nodes = error['generated_nodes'] - set((good_node, ))

        if args.output_ignore_list:
            for generated_node in bad_nodes:
                for wire in generated_node:
                    ignored_wires.add(wire)

            continue

        if max(len(generated_node) for generated_node in bad_nodes) > 1:
            assert False, node
        else:
            not_pcie = False
            for generated_node in bad_nodes:
                for wire in generated_node:
                    if not wire.startswith('PCIE'):
                        not_pcie = True
            if not_pcie:
                #print(node, good_node, map(tuple, bad_nodes))
                print(repr((node, tuple(map(tuple, bad_nodes)))))
                pass
            else:
                #print(repr((node, map(tuple, bad_nodes))))
                pass

    if args.output_ignore_list:
        for wire in ignored_wires:
            print(wire)


if __name__ == '__main__':
    main()
