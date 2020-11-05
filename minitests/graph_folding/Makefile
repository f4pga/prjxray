# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
DB_ROOT ?= ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}
PART ?= ${XRAY_PART}
DATABASE ?= build_${PART}/${PART}.db
WIRE_PATTERNS ?= build_${PART}/wire_patterns.bin

all: build_${PART}/wire_patterns.bin

build_${PART}:
	mkdir -p build_${PART}

${DATABASE}: build_node_lookup.py node_lookup.py | build_${PART}
	python3 build_node_lookup.py \
		--db-root ${DB_ROOT} \
		--part ${PART} \
		${DATABASE}

.PHONY: clean database build_patterns check_patterns print_size

database: ${DATABASE}

build_patterns: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--tile &> build_${PART}/node_to_wires.log
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--wire_to_node \
				--tile &> build_${PART}/wire_to_node.log

check_patterns:
	/usr/bin/time -v python3 check_patterns.py \
		--database ${DATABASE} \
		--output_dir build_${PART}/

print_size:
	python3 sum_all_patterns.py --output_dir build_${PART}

clean:
	rm -rf build_${PART}
