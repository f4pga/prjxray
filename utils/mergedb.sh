#!/bin/bash
set -ex
test $# = 2
test -e "$1"
touch "$2"
tmp=`mktemp -p .`
sort -u "$1" "$2" | grep -v '<.*>' > "$tmp"
mv "$tmp" "$2"
