#!/usr/bin/env bash
set -ex
MAKE=${MAKE:-make}
MAKEFLAGS=${MAKEFLAGS:-}
echo "make: ${MAKE} ${MAKEFLAGS}"
echo $MAKE
mkdir -p todo;
while
    ${MAKE} ${MAKEFLAGS} cleanprj;
    ${MAKE} ${MAKEFLAGS} build/todo.txt || exit 1;
    test -s build/todo.txt;
do
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

