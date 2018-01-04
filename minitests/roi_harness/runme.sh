#!/bin/bash

set -ex
vivado -mode batch -source runme.tcl
test -z "$(fgrep CRITICAL vivado.log)"

