#!/bin/bash

GITHUB_PROTO=${1:-git+ssh}
GITHUB_URL=$GITHUB_PROTO://github.com/SymbiFlow/prjxray-db-xc7.git
rm -rf database
git clone $GITHUB_URL database
