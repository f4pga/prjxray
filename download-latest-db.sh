#!/usr/bin/env bash

GITHUB_PROTO=${1:-https}
GITHUB_URL=$GITHUB_PROTO://github.com/SymbiFlow/prjxray-db.git
rm -rf database
git clone $GITHUB_URL database
# Update files in the database from our version so fuzzers run correctly.
git checkout HEAD database
