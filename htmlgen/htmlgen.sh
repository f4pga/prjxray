#!/bin/bash

DATABASE=$1

# If DATABASE is empty, checks htmlgen for all settings files
SETTINGS=../settings/$DATABASE*.sh

for setting in $SETTINGS
do
    no_prefix_setting=${setting#../settings/}
    clean_setting=${no_prefix_setting%.sh}
    echo ""
    echo "============================================="
    echo "Generating HTML for ${clean_setting}"
    echo "============================================="
    echo ""
    source ../settings/$setting
    ./htmlgen.py --output html/${clean_setting}
done
