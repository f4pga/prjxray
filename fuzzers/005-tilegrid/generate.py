#!/usr/bin/env python3

import os, sys, json, re

database = dict()

tiles = list()
site_baseaddr = dict()

with open("tiles.txt") as f:
    for line in f:
        tiles.append(line.split())

for arg in sys.argv[1:]:
    with open(arg) as f:
        line = f.read().strip()
        site = arg[7:-6]
        frame = int(line[5:5+8], 16)
        site_baseaddr[site] = "0x%08x" % (frame & ~0x7f)

# print(json.dumps(database, sort_keys=True, indent="\t"))
# print(json.dumps(tiles, sort_keys=True, indent="\t"))
print(json.dumps(site_baseaddr, sort_keys=True, indent="\t"))

