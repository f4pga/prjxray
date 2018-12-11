#!/usr/bin/env bash
set -ex
MAKE=${MAKE:-make}
MAKEFLAGS=${MAKEFLAGS:-}
echo "make: ${MAKE} ${MAKEFLAGS}"
echo $MAKE
mkdir -p todo;
while true; do
    ${MAKE} ${MAKEFLAGS} cleanprj;
    ${MAKE} ${MAKEFLAGS} build/todo.txt || exit 1;
    echo "Remaining: " $(wc -l build/todo_all.txt)
    if [ \! -s build/todo.txt ] ; then
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

