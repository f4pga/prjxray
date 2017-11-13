#!/usr/bin/env python3

import os, sys, json, re


#######################################
# Read

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


#######################################
# Create initial database

database = dict()
database["tiles"] = dict()
database["segments"] = dict()
tiles_by_grid = dict()

for record in tiles:
    tile_type, tile_name, grid_x, grid_y = record[0:4]
    grid_x, grid_y = int(grid_x), int(grid_y)
    tiles_by_grid[(grid_x, grid_y)] = tile_name
    framebaseaddr = None

    database["tiles"][tile_name] = {
        "type": tile_type,
        "grid_x": grid_x,
        "grid_y": grid_y
    }

    if len(record) > 4:
        database["tiles"][tile_name]["sites"] = dict()
        for i in range(4, len(record), 2):
            site_type, site_name = record[i:i+2]
            if site_name in site_baseaddr:
                framebaseaddr = site_baseaddr[site_name]
            database["tiles"][tile_name]["sites"][site_name] = site_type

    if tile_type in ["CLBLL_L", "CLBLL_R", "CLBLM_L", "CLBLM_R"]:
        segment_name = "SEG_" + tile_name
        segtype = tile_type.lower()
        database["segments"][segment_name] = dict()
        database["segments"][segment_name]["tiles"] = [tile_name]
        database["segments"][segment_name]["type"] = segtype
        database["segments"][segment_name]["frames"] = 36
        database["segments"][segment_name]["words"] = 2
        if framebaseaddr is not None:
            database["segments"][segment_name]["baseaddr"] = [framebaseaddr, 0]
        database["tiles"][tile_name]["segment"] = segment_name


#######################################
# Pupulate segment base addresses

start_segments = list()

for segment_name in database["segments"].keys():
    if "baseaddr" in database["segments"][segment_name]:
        start_segments.append(segment_name)

for segment_name in start_segments:
    framebase, wordbase = database["segments"][segment_name]["baseaddr"]
    clbtile = [tile for tile in database["segments"][segment_name]["tiles"] if tile.startswith("CLBL")][0]
    grid_x = database["tiles"][clbtile]["grid_x"]
    grid_y = database["tiles"][clbtile]["grid_y"]

    for i in range(49):
        while True:
            grid_y -= 1
            clbtile = tiles_by_grid[(grid_x, grid_y)]
            if clbtile.startswith("CLBL"): break

        wordbase += 2
        if wordbase == 50: wordbase += 1

        segname = database["tiles"][clbtile]["segment"]
        database["segments"][segname]["baseaddr"] = [framebase, wordbase]


#######################################
# Add INT tiles to segments

for segment_name in database["segments"].keys():
    for clbtile in database["segments"][segment_name]["tiles"]:
        if not clbtile.startswith("CLBL"):
            continue

        grid_x = database["tiles"][clbtile]["grid_x"]
        grid_y = database["tiles"][clbtile]["grid_y"]

        if database["tiles"][clbtile]["type"] in ["CLBLL_L", "CLBLM_L"]:
            grid_x += 1
        else:
            grid_x -= 1

        inttile = tiles_by_grid[(grid_x, grid_y)]
        assert inttile.startswith("INT_")

        database["tiles"][inttile]["segment"] = segment_name
        s = set(database["segments"][segment_name]["tiles"] + [inttile])
        database["segments"][segment_name]["tiles"] = list(sorted(s))


#######################################
# Write

print(json.dumps(database, sort_keys=True, indent="\t"))

