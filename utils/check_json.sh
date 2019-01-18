#!/bin/bash -e

# check_json.sh <database a> <database b>
#
# Tool for comparing database JSON outputs from two database's.

DIR_A=$1
DIR_B=$2

for A_JSON_IN in $( ls ${DIR_A}/*.json ); do
    A_JSON_OUT="$(mktemp)_a"
    B_JSON_OUT="$(mktemp)_b"

    B_JSON_IN="${DIR_B}/$(basename ${A_JSON_IN})"

    if [ ! -f "${B_JSON_IN}" ]; then
        echo "${B_JSON_IN} not found!"
        continue
    fi

    python3 -m utils.xjson ${A_JSON_IN} > ${A_JSON_OUT}
    python3 -m utils.xjson ${B_JSON_IN} > ${B_JSON_OUT}

    echo "Comparing $(basename ${A_JSON_IN})"
    diff -U 3 ${A_JSON_OUT} ${B_JSON_OUT} || true
done
