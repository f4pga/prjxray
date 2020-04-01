#!/bin/bash

SETTINGS=../settings/*

for setting in $SETTINGS
do
    echo ""
    echo "============================================="
    echo "Generating HTML for ${setting%.sh}"
    echo "============================================="
    echo ""
    source ../settings/$setting
    ./htmlgen.py
done
