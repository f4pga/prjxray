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

${WIRE_PATTERNS}: test_reduction.py ${DATABASE}
	python3 test_reduction.py \
		--database ${DATABASE} \
		--wire_patterns ${WIRE_PATTERNS}

.PHONY: clean database wire_patterns

database: ${DATABASE}
.PHONY: clean database build_patterns check_patterns print_size
 
database: ${DATABASE}

build_patterns: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--only_pips \
				--tile &> build_${PART}/node_to_pip_wires.log
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--wire_to_node \
				--tile &> build_${PART}/wire_to_node.log
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
				--nodes_and_wires \
				--tile &> build_${PART}/nodes_and_wires.log
check_patterns:
	/usr/bin/time -v python3 check_patterns.py \
		--database ${DATABASE} \
		--output_dir build_${PART}/

wire_patterns: ${WIRE_PATTERNS}

clean:
	rm -rf build_${PART}

one_pattern: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--only_pips \
				--tile ${TILE} \
			
node_to_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--tile ${TILE} \

pip_node_to_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--only_pips \
				--tile ${TILE} \

wire_to_node: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--wire_to_node \
				--tile ${TILE} \

nodes_and_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--nodes_and_wires \
				--tile ${TILE} \

nodes_and_pip_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--nodes_and_wires \
				--only_pips \
				--tile ${TILE} \


1_node_to_pip_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--only_pips \
				--tile &> build_${PART}/node_to_pip_wires.log

2_wire_to_node: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--wire_to_node \
				--tile &> build_${PART}/wire_to_node.log

3_node_to_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--node_to_wires \
				--tile &> build_${PART}/node_to_wires.log

4_nodes_and_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--nodes_and_wires \
				--tile &> build_${PART}/nodes_and_wires.log

5_nodes_and_pip_wires: ${DATABASE} reduce_graph_for_type.py distributed_bsc.py reference_model.py
	python3 print_tile_types.py | \
		/usr/bin/time -v xargs -n1 \
			/usr/bin/time -v python3 reduce_graph_for_type.py \
				--database ${DATABASE} \
				--output_dir build_${PART} \
				--nodes_and_wires \
				--only_pips \
				--tile &> build_${PART}/nodes_and_wires.log
