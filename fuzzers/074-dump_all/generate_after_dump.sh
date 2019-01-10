#!/bin/bash -xe

rm -rf build/output
mkdir -p build/output
python3 reduce_tile_types.py \
  --root_dir build/specimen_001/ \
  --output_dir build/output
python3 create_node_tree.py \
  --dump_all_root_dir build/specimen_001/ \
  --ordered_wires_root_dir ../072-ordered_wires/build/specimen_001/ \
  --output_dir build/output
python3 reduce_site_types.py --output_dir build/output
python3 generate_grid.py --root_dir build/specimen_001/ --output_dir build/output \
  --ignored_wires ${XRAY_DATABASE}_ignored_wires.txt
