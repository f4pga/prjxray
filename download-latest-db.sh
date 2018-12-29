#!/usr/bin/env bash

GITHUB_PROTO=${1:-https}
GITHUB_URL=$GITHUB_PROTO://github.com/SymbiFlow/prjxray-db.git
rm -rf database
git clone $GITHUB_URL database
# Causes confusion if you try to commit in DB dir
# But doesn't effect most people, probably leave as is
# rm -rf database/.git
# travis, .gitignore, etc
rm -f database/* 2>/dev/null
rm -f database/.* 2>/dev/null
# Restore settings files so fuzzers run correctly
git checkout HEAD database
