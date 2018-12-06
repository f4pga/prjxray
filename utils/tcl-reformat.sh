#!/usr/bin/env bash
# Wrapper to clean up newlines
# We could do this in tcl...but tcl

fn=$1

$XRAY_REFORMAT_TCL $fn >/dev/null
# Always puts a newline at the end, even if there was one before
# remove duplicates, but keep at least one
printf "%s\n" "$(< $fn)" >$fn.tmp
mv $fn.tmp $fn

# Remove trailing spaces
sed -i 's/[ \t]*$//' "$fn"

