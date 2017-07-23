#!/usr/bin/env python3

import sys
import json
import re

db_tiles = set()
db_tile_prop = dict()
db_tile_sites = dict()

db_sites = set()
db_site_prop = dict()
db_site_tile = dict()
db_site_bit = dict()

def add_tile(tile):
    if tile not in db_tiles:
        db_tiles.add(tile)
        db_tile_prop[tile] = dict()
        db_tile_sites[tile] = list()

def add_site(site):
    if site not in db_sites:
        db_sites.add(site)
        db_site_prop[site] = dict()

with open("%s.txt" % sys.argv[1]) as f:
    for line in f:
        line = line.split()

        if line[0] == "TILEPROP":
            add_tile(line[1])
            db_tile_prop[line[1]][line[2]] = " ".join(line[3:])
            continue

        if line[0] == "TILESITE":
            add_tile(line[1])
            add_site(line[2])
            db_tile_sites[line[1]].append(line[2])
            db_site_tile[line[2]] = line[1]
            continue

        if line[0] == "SITEPROP":
            add_site(line[1])
            db_site_prop[line[1]][line[2]] = " ".join(line[3:])
            continue

        if line[0] == "SLICEBIT":
            for i in range(50):
                assert line[1] not in db_site_bit
                db_site_bit[line[1]] = line[2] + ("" if i == 0 else " ?")
                m = re.match("(.*)Y([0-9]+)", line[1])
                line[1] = "%sY%d" % (m.group(1), int(m.group(2))+1)
            continue

        assert False

print("Number of tiles: %d" % len(db_tiles))
print("Number of sites: %d" % len(db_sites))
print("Number of sites with bit: %d" % len(db_site_bit))

database = dict()

database["tiles"] = dict()
for tile in db_tiles:
    entry = dict()
    entry["props"] = db_tile_prop[tile]
    entry["sites"] = db_tile_sites[tile]
    database["tiles"][tile] = entry

database["sites"] = dict()
for site in db_sites:
    entry = dict()
    entry["props"] = db_site_prop[site]
    entry["tile"] = db_site_tile[site]
    if site in db_site_bit:
        entry["bit"] = db_site_bit[site]
    database["sites"][site] = entry

with open("%s.json" % sys.argv[1], "w") as f:
    print(json.dumps(database, sort_keys=True, indent="\t"), file=f)

