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
import os
from stat import S_ISDIR


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--output_dir', required=True)

    args = parser.parse_args()

    sum_node_to_wires = 0
    sum_node_to_pip_wires = 0
    sum_wire_to_nodes = 0
    sum_nodes_and_wires = 0
    sum_nodes_and_pip_wires = 0

    num_node_to_wires = 0
    num_node_to_pip_wires = 0
    num_wire_to_nodes = 0
    num_nodes_and_wires = 0
    num_nodes_and_pip_wires = 0

    for fname in os.listdir(args.output_dir):
        file_stats = os.stat(os.path.join(args.output_dir, fname))

        if S_ISDIR(file_stats.st_mode):
            continue

        if fname.endswith('_node_to_pip_wires.bin'):
            sum_node_to_pip_wires += file_stats.st_size
            num_node_to_pip_wires += 1

        if fname.endswith('_node_to_wires.bin'):
            sum_node_to_wires += file_stats.st_size
            num_node_to_wires += 1

        if fname.endswith('_wire_to_nodes.bin'):
            sum_wire_to_nodes += file_stats.st_size
            num_wire_to_nodes += 1
        if fname.endswith('_nodes_and_wires.bin'):
            sum_nodes_and_wires += file_stats.st_size
            num_nodes_and_wires += 1
        if fname.endswith('_nodes_and_pip_wires.bin'):
            sum_nodes_and_pip_wires += file_stats.st_size
            num_nodes_and_pip_wires += 1

    MIL = 1048576
    print(f'Wire to nodes ({num_wire_to_nodes}): {sum_wire_to_nodes/MIL:.2f}MB')
    print(f'Node to pip wires ({num_node_to_pip_wires}): {sum_node_to_pip_wires/MIL:.2f}MB')
    print(f'Node to wires ({num_node_to_wires}): {sum_node_to_wires/MIL:.2f}MB')
    print(f'Nodes and wires ({num_nodes_and_wires}): {sum_nodes_and_wires/MIL:.2f}MB')
    print(f'Nodes and pip wires ({num_nodes_and_pip_wires}): {sum_nodes_and_pip_wires/MIL:.2f}MB')


if __name__ == '__main__':
    main()
