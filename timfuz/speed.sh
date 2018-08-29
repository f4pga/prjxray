#!/usr/bin/env bash
set -ex

mkdir -p build_speed
cd build_speed
vivado -mode batch -source ../speed.tcl
python ../speed_json.py speed_model.txt node.txt speed.json

