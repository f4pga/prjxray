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

    for fname in os.listdir(args.output_dir):
        file_stats = os.stat(os.path.join(args.output_dir, fname))

        if S_ISDIR(file_stats.st_mode):
            continue

        if fname.endswith('_node_to_pip_wires.bin'):
            sum_node_to_pip_wires += file_stats.st_size

        if fname.endswith('_node_to_wires.bin'):
            sum_node_to_wires += file_stats.st_size

        if fname.endswith('_wire_to_nodes.bin'):
            sum_wire_to_nodes += file_stats.st_size

    print('Wire to nodes (bytes): ', sum_wire_to_nodes)
    print('Node to pip wires (bytes): ', sum_node_to_pip_wires)
    print('Node to wires (bytes): ', sum_node_to_wires)


if __name__ == '__main__':
    main()
