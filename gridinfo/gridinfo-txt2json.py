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
            db_site_bit[line[1]] = line[2]
            continue

        assert False

print("Number of tiles: %d" % len(db_tiles))
print("Number of sites: %d" % len(db_sites))
print("Number of sites with bit: %d" % len(db_site_bit))

database = dict()
loc_to_tile = dict()

database["device"] = sys.argv[2]

database["tiles"] = dict()
for tile in db_tiles:
    entry = dict()
    entry["props"] = db_tile_prop[tile]
    entry["sites"] = db_tile_sites[tile]
    database["tiles"][tile] = entry

    col = int(db_tile_prop[tile]["COLUMN"])
    row = int(db_tile_prop[tile]["ROW"])
    loc_to_tile[(col, row)] = tile

database["sites"] = dict()
for site in db_sites:
    entry = dict()
    entry["props"] = db_site_prop[site]
    entry["tile"] = db_site_tile[site]
    database["sites"][site] = entry

for site, bit in db_site_bit.items():
    bit = bit.split("_")
    bit_type = int(bit[4][1:])
    bit_half = int(bit[5][1:])
    bit_row = int(bit[6][1:])
    bit_col = int(bit[7][1:])
    bit_word = int(bit[9][1:])
    assert len(bit) == 11

    for i in range(50):
        m = re.match("(.*)Y([0-9]+)", site)
        this_site = "%sY%d" % (m.group(1), int(m.group(2))+i)

        tile = db_site_tile[this_site]

        word = bit_word + 2*i
        if word >= 50: word += 1

        entry = dict()
        entry["BASE_FRAMEID"] = "0x%08x" % ((bit_type << 23) | (bit_half << 22) | (bit_row << 17) | (bit_col << 7))
        entry["FRAME_TYPE"] = bit_type
        entry["FRAME_HALF"] = bit_half
        entry["FRAME_ROW"] = bit_row
        entry["FRAME_COLUMN"] = bit_col
        entry["WORDS"] = [word, word+1]

        database["tiles"][tile]["cfgcol"] = entry

        if database["tiles"][tile]["props"]["TILE_TYPE"] in ("CLBLL_L", "CLBLM_L"):
            col = int(db_tile_prop[tile]["COLUMN"])
            row = int(db_tile_prop[tile]["ROW"])
            right_tile = loc_to_tile[(col+1, row)]

            database["tiles"][right_tile]["cfgcol"] = entry

        if database["tiles"][tile]["props"]["TILE_TYPE"] in ("CLBLL_R", "CLBLM_R"):
            col = int(db_tile_prop[tile]["COLUMN"])
            row = int(db_tile_prop[tile]["ROW"])
            left_tile = loc_to_tile[(col-1, row)]

            database["tiles"][left_tile]["cfgcol"] = entry

tile_cfgcol_count = 0
cfgcols = set()

for tile in db_tiles:
    if "cfgcol" in database["tiles"][tile]:
        cfgcols.add(database["tiles"][tile]["cfgcol"]["BASE_FRAMEID"])
        tile_cfgcol_count += 1

print("Number of assigned columns: %d" % len(cfgcols))
print("Number of tiles with assigned column: %d" % tile_cfgcol_count)

with open("%s.json" % sys.argv[1], "w") as f:
    print(json.dumps(database, sort_keys=True, indent="\t"), file=f)

