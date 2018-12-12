#!/usr/bin/env bash

usage() {
    echo "Run makefile until termination condition"
    echo "usage: int_loop.sh [args]"
    echo "--check-args <args>         int_loop_check.py args"
    # intpips ingests all segbits files at once and does a push at the end
    # other loopers do a push every pass
    echo "--iter-pushdb               make pushdb after successful make database as opposed to end"
}

check_args=
iter_pushdb=false
end_pushdb=true
while [[ $# -gt 0 ]]; do
    case "$1" in
    --check-args)
        check_args=$2
        shift
        shift
        ;;
    --iter-pushdb)
        iter_pushdb=true
        end_pushdb=false
        shift
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unrecognized argument"
        usage
        exit 1
        ;;
    esac
done

# Quick solves are sloppy
# Never push them in as they may be under solved
if [ "$QUICK" = "Y" ] ; then
    iter_pushdb=false
    end_pushdb=false
fi

set -ex
MAKE=${MAKE:-make}
echo $MAKE
mkdir -p todo;
i=1
while true; do
    ${MAKE} ITER=$i cleanprj
    ${MAKE} ITER=$i build/todo.txt
    if python3 ${XRAY_DIR}/fuzzers/int_loop_check.py $check_args ; then
        break
    fi
    if [ -f todo/timeout ] ; then
        echo "ERROR: timeout"
        exit 1
    fi

    cp build/todo.txt todo/${i}.txt;
    cp build/todo_all.txt todo/${i}_all.txt;
    if ${MAKE} ITER=$i database; then
        if $iter_pushdb ; then
            ${MAKE} pushdb
        fi
    fi;
    if [ "$QUICK" = "Y" ] ; then
        break;
    fi

    i=$((i+1));
done;
if $end_pushdb ; then
    ${MAKE} pushdb
fi
exit 0

