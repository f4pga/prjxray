#!/usr/bin/env python3

import os, sys, json, re


#######################################
# Read

tiles = list()
site_baseaddr = dict()
tile_baseaddr = dict()

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
        "sites": dict(),
        "grid_x": grid_x,
        "grid_y": grid_y
    }

    if len(record) > 4:
        for i in range(4, len(record), 2):
            site_type, site_name = record[i:i+2]
            if site_name in site_baseaddr:
                framebaseaddr = site_baseaddr[site_name]
            database["tiles"][tile_name]["sites"][site_name] = site_type

    if framebaseaddr is not None:
        tile_baseaddr[tile_name] = [framebaseaddr, 0]


#######################################
# Add Segments

for tile_name, tile_data in database["tiles"].items():
    tile_type = tile_data["type"]
    grid_x = tile_data["grid_x"]
    grid_y = tile_data["grid_y"]

    if tile_type in ["CLBLL_L", "CLBLL_R", "CLBLM_L", "CLBLM_R"]:
        if tile_type in ["CLBLL_L", "CLBLM_L"]:
            int_tile_name = tiles_by_grid[(grid_x+1, grid_y)]
        else:
            int_tile_name = tiles_by_grid[(grid_x-1, grid_y)]

        segment_name = "SEG_" + tile_name
        segtype = tile_type.lower()

        database["segments"][segment_name] = dict()
        database["segments"][segment_name]["tiles"] = [tile_name, int_tile_name]
        database["segments"][segment_name]["type"] = segtype
        database["segments"][segment_name]["frames"] = 36
        database["segments"][segment_name]["words"] = 2

        if tile_name in tile_baseaddr:
            database["segments"][segment_name]["baseaddr"] = tile_baseaddr[tile_name]

        database["tiles"][tile_name]["segment"] = segment_name
        database["tiles"][int_tile_name]["segment"] = segment_name

    if tile_type in ["HCLK_L", "HCLK_R"]:
        segment_name = "SEG_" + tile_name
        segtype = tile_type.lower()

        database["segments"][segment_name] = dict()
        database["segments"][segment_name]["tiles"] = [tile_name]
        database["segments"][segment_name]["type"] = segtype
        database["segments"][segment_name]["frames"] = 26
        database["segments"][segment_name]["words"] = 1
        database["tiles"][tile_name]["segment"] = segment_name

    if tile_type in ["BRAM_L", "DSP_L", "BRAM_R", "DSP_R"]:
        for k in range(5):
            if tile_type in ["BRAM_L", "DSP_L"]:
                interface_tile_name = tiles_by_grid[(grid_x+1, grid_y-k)]
                int_tile_name = tiles_by_grid[(grid_x+2, grid_y-k)]
            else:
                interface_tile_name = tiles_by_grid[(grid_x-1, grid_y-k)]
                int_tile_name = tiles_by_grid[(grid_x-2, grid_y-k)]

            segment_name = "SEG_" + tile_name.replace("_", "%d_" % k, 1)
            segtype = tile_type.lower().replace("_", "%d_" % k, 1)

            database["segments"][segment_name] = dict()
            database["segments"][segment_name]["type"] = segtype
            database["segments"][segment_name]["frames"] = 28
            database["segments"][segment_name]["words"] = 1

            if k == 0:
                database["segments"][segment_name]["tiles"] = [tile_name, interface_tile_name, int_tile_name]
                database["tiles"][tile_name]["segment"] = segment_name
                database["tiles"][interface_tile_name]["segment"] = segment_name
                database["tiles"][int_tile_name]["segment"] = segment_name
            else:
                database["segments"][segment_name]["tiles"] = [interface_tile_name, int_tile_name]
                database["tiles"][interface_tile_name]["segment"] = segment_name
                database["tiles"][int_tile_name]["segment"] = segment_name


#######################################
# Populate segment base addresses: L/R along INT column

for segment_name in database["segments"].keys():
    if "baseaddr" in database["segments"][segment_name]:
        framebase, wordbase = database["segments"][segment_name]["baseaddr"]
        inttile = [tile for tile in database["segments"][segment_name]["tiles"] if database["tiles"][tile]["type"] in ["INT_L", "INT_R"]][0]
        grid_x = database["tiles"][inttile]["grid_x"]
        grid_y = database["tiles"][inttile]["grid_y"]

        if database["tiles"][inttile]["type"] == "INT_L":
            grid_x += 1
            framebase = "0x%08x" % (int(framebase, 16) + 0x80)
        else:
            grid_x -= 1
            framebase = "0x%08x" % (int(framebase, 16) - 0x80)

        if (grid_x, grid_y) not in tiles_by_grid:
            continue

        tile = tiles_by_grid[(grid_x, grid_y)]

        if database["tiles"][inttile]["type"] == "INT_L":
            assert database["tiles"][tile]["type"] == "INT_R"
        elif database["tiles"][inttile]["type"] == "INT_R":
            assert database["tiles"][tile]["type"] == "INT_L"
        else:
            assert 0

        assert "segment" in database["tiles"][tile]

        seg = database["tiles"][tile]["segment"]

        if "baseaddr" in database["segments"][seg]:
            assert database["segments"][seg]["baseaddr"] == [framebase, wordbase]
        else:
            database["segments"][seg]["baseaddr"] = (framebase, wordbase)


#######################################
# Populate segment base addresses: Up along INT/HCLK columns

start_segments = list()

for segment_name in database["segments"].keys():
    if "baseaddr" in database["segments"][segment_name]:
        start_segments.append(segment_name)

for segment_name in start_segments:
    framebase, wordbase = database["segments"][segment_name]["baseaddr"]
    inttile = [tile for tile in database["segments"][segment_name]["tiles"] if database["tiles"][tile]["type"] in ["INT_L", "INT_R"]][0]
    grid_x = database["tiles"][inttile]["grid_x"]
    grid_y = database["tiles"][inttile]["grid_y"]

    for i in range(50):
        grid_y -= 1

        if wordbase == 50:
            wordbase += 1
        else:
            wordbase += 2

        segname = database["tiles"][tiles_by_grid[(grid_x, grid_y)]]["segment"]
        database["segments"][segname]["baseaddr"] = [framebase, wordbase]


#######################################
# Write

print(json.dumps(database, sort_keys=True, indent="\t"))

