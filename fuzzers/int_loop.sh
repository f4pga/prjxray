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

set -ex
MAKE=${MAKE:-make}
MAKEFLAGS=${MAKEFLAGS:-}
echo "make: ${MAKE} ${MAKEFLAGS}"
echo $MAKE
mkdir -p todo;
i=1
while true; do
    ${MAKE} ${MAKEFLAGS} ITER=$i cleanprj
    ${MAKE} ${MAKEFLAGS} ITER=$i build/todo.txt
    if python3 ${XRAY_DIR}/fuzzers/int_loop_check.py $check_args ; then
        break
    fi
    if [ -f todo/timeout ] ; then
        echo "ERROR: timeout"
        exit 1
    fi

    cp build/todo.txt todo/${i}.txt;
    cp build/todo_all.txt todo/${i}_all.txt;
    if ${MAKE} ${MAKEFLAGS} ITER=$i database; then
        if $iter_pushdb ; then
            ${MAKE} ${MAKEFLAGS} pushdb
        fi
    fi;
    if [ "$QUICK" = "Y" ] ; then
        break;
    fi

    i=$((i+1));
done;
if $end_pushdb ; then
    ${MAKE} ${MAKEFLAGS} pushdb
fi
exit 0

