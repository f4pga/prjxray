#!/bin/bash -xe
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# By default use ~50 GiB for generate_grid.py, but allow override.
export DEFAULT_MAX_GRID_CPU=10

export BUILD_DIR=build_${XRAY_PART}
rm -rf ${BUILD_DIR}/output
mkdir -p ${BUILD_DIR}/output
python3 reduce_tile_types.py \
  --root_dir ${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output
python3 create_node_tree.py \
  --dump_all_root_dir ${BUILD_DIR}/specimen_001/ \
  --ordered_wires_root_dir ../072-ordered_wires/${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output
python3 reduce_site_types.py --output_dir ${BUILD_DIR}/output
python3 generate_grid.py \
  --root_dir ${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output \
  --ignored_wires ignored_wires/${XRAY_DATABASE}/${XRAY_PART}_ignored_wires.txt \
  --max_cpu=${MAX_GRID_CPU:-${DEFAULT_MAX_GRID_CPU}}
python3 node_names.py \
  --root_dir ${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output/ \
  --max_cpu=${MAX_GRID_CPU:-${DEFAULT_MAX_GRID_CPU}}
python3 check_nodes.py \
  --root_dir ${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output/ \
  --ignored_wires ignored_wires/${XRAY_DATABASE}/${XRAY_PART}_ignored_wires.txt \
  --max_cpu=${MAX_GRID_CPU:-${DEFAULT_MAX_GRID_CPU}}
