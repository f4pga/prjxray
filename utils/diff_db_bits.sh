#!/bin/bash -e

# diff_db_bits.sh <database a> <database b>
#
# Tool for comparing database segbits outputs from two database's.

DIR_A=$1
DIR_B=$2

for A_DB_IN in $( ls ${DIR_A}/segbits*.db ); do
    A_DB_OUT="$(mktemp)_a_$(basename ${A_DB_IN})"
    B_DB_OUT="$(mktemp)_b_$(basename ${A_DB_IN})"

    B_DB_IN="${DIR_B}/$(basename ${A_DB_IN})"

    if [ ! -f "${B_DB_IN}" ]; then
        echo "${B_DB_IN} not found!"
        continue
    fi

    sort ${A_DB_IN} > ${A_DB_OUT}
    sort ${B_DB_IN} > ${B_DB_OUT}

    echo "Comparing $(basename ${A_DB_IN})"
    diff -U 0 ${A_DB_OUT} ${B_DB_OUT} || true
done
