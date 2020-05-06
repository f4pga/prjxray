#!/bin/bash

echo
echo "==================================="
echo "Check python utf coding and shebang"
echo "==================================="
echo

ERROR_FILES_SHEBANG=""
ERROR_FILES_UTF_CODING=""
FILES_TO_CHECK=`find . \
    -size +0 -type f \( -name '*.py' \) \
    \( -not -path "*/.*/*" -not -path "*/third_party/*" -not -path "*/env/*" \)`

for file in $FILES_TO_CHECK; do
    echo "Checking $file"
    if [[ -x $file ]]; then
        grep -q "\#\!/usr/bin/env python3" $file || ERROR_FILES_SHEBANG="$ERROR_FILES_SHEBANG $file"
    fi
    grep -q "\#.*coding: utf-8" $file || ERROR_FILES_UTF_CODING="$ERROR_FILES_UTF_CODING $file"
done

if [ ! -z "$ERROR_FILES_SHEBANG" ]; then
    for file in $ERROR_FILES_SHEBANG; do
        echo "ERROR: $file does not have the python3 shebang."
    done
    return 1
fi

if [ ! -z "$ERROR_FILES_UTF_CODING" ]; then
    for file in $ERROR_FILES_UTF_CODING; do
        echo "ERROR: $file does not have the utf encoding set."
    done
    return 1
fi

echo
