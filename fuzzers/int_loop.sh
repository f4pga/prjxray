#!/usr/bin/env bash

usage() {
    echo "Run makefile until termination condition"
    echo "usage: int_loop.sh [args]"
    echo "--check-args <args>         int_loop_check.py args"
}

check_args=
while [[ $# -gt 0 ]]; do
    case "$1" in
    --check-args)
        check_args=$2
        shift
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
while true; do
    ${MAKE} ${MAKEFLAGS} cleanprj;
    ${MAKE} ${MAKEFLAGS} build/todo.txt || exit 1;
    if python3 ${XRAY_DIR}/fuzzers/int_loop_check.py $check_args ; then
        break
    fi

    i=$((i+1));
    cp build/todo.txt todo/${i}.txt;
    cp build/todo_all.txt todo/${i}_all.txt;
    if ${MAKE} ${MAKEFLAGS} database; then
        ${MAKE} ${MAKEFLAGS} pushdb;
    fi;
    if [ "$QUICK" = "Y" ] ; then
        break;
    fi
done;
exit 0

