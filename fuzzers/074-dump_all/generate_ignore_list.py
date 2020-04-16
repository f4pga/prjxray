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

with open('output/error_nodes.json') as f:
    flat_error_nodes = json.load(f)

error_nodes = {}
for node, raw_node, generated_nodes in flat_error_nodes:
    if node not in error_nodes:
        error_nodes[node] = {
            'raw_node': set(raw_node),
            'generated_nodes': set(),
        }

    assert error_nodes[node]['raw_node'] == set(raw_node)
    error_nodes[node]['generated_nodes'].add(tuple(sorted(generated_nodes)))

for node, error in error_nodes.items():
    combined_generated_nodes = set()
    for generated_node in error['generated_nodes']:
        combined_generated_nodes |= set(generated_node)

    assert error['raw_node'] == combined_generated_nodes, (node, error)

    good_node = max(error['generated_nodes'], key=lambda x: len(x))
    bad_nodes = error['generated_nodes'] - set((good_node, ))

    if max(len(generated_node) for generated_node in bad_nodes) > 1:
        assert False, node
    else:
        for generated_node in bad_nodes:
            for wire in generated_node:
                print(wire)
