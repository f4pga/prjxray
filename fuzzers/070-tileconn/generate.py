#!/usr/bin/env python3

import os, sys, json, re

tilenodes = dict()
grid2tile = dict()
database = dict()

print("Loading %s grid." % os.getenv("XRAY_DATABASE"))
with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")), "r") as f:
    grid = json.load(f)

for tile, tiledata in grid["tiles"].items():
    grid_xy = (tiledata["grid_x"], tiledata["grid_y"])
    grid2tile[grid_xy] = tile

print("Loading nodewires.txt.")
with open("nodewires.txt") as f:
    for line in f:
        node, *wires = line.split()
        for wire in wires:
            wire_tile, wire_name = wire.split("/")
            if wire_tile not in tilenodes:
                tilenodes[wire_tile] = dict()
            tilenodes[wire_tile][node] = wire_name

def filter_pair(type1, type2, wire1, wire2, delta_x, delta_y):
    if type1 in ["HCLK_L", "HCLK_R"]:
        is_vertical_wire = False
        if wire1.startswith("HCLK_S"): is_vertical_wire = True
        if wire1.startswith("HCLK_N"): is_vertical_wire = True
        if wire1.startswith("HCLK_W"): is_vertical_wire = True
        if wire1.startswith("HCLK_E"): is_vertical_wire = True
        if wire1.startswith("HCLK_LV"): is_vertical_wire = True
        if wire1.startswith("HCLK_BYP"): is_vertical_wire = True
        if wire1.startswith("HCLK_FAN"): is_vertical_wire = True
        if wire1.startswith("HCLK_LEAF_CLK_"): is_vertical_wire = True
        if is_vertical_wire and delta_y == 0: return True
        if not is_vertical_wire and delta_x == 0: return True

    return False

def handle_pair(tile1, tile2):
    if tile1 not in tilenodes: return
    if tile2 not in tilenodes: return

    tile1data = grid["tiles"][tile1]
    tile2data = grid["tiles"][tile2]

    grid1_xy = (tile1data["grid_x"], tile1data["grid_y"])
    grid2_xy = (tile2data["grid_x"], tile2data["grid_y"])

    if grid1_xy > grid2_xy:
        return handle_pair(tile2, tile1)

    key = (tile1data["type"], tile2data["type"], grid2_xy[0] - grid1_xy[0], grid2_xy[1] - grid1_xy[1])

    wire_pairs = set()

    for node, wire1 in tilenodes[tile1].items():
        if node in tilenodes[tile2]:
            wire2 = tilenodes[tile2][node]
            if filter_pair(key[0], key[1], wire1, wire2, key[2], key[3]):
                continue
            if filter_pair(key[1], key[0], wire2, wire1, -key[2], -key[3]):
                continue
            wire_pairs.add((wire1, wire2))

    if key not in database:
        database[key] = wire_pairs
    else:
        database[key] &= wire_pairs

for tile, tiledata in grid["tiles"].items():
    grid_right_xy = (tiledata["grid_x"]+1, tiledata["grid_y"])
    grid_below_xy = (tiledata["grid_x"], tiledata["grid_y"]+1)

    if grid_right_xy in grid2tile:
        handle_pair(tile, grid2tile[grid_right_xy])

    if grid_below_xy in grid2tile:
        handle_pair(tile, grid2tile[grid_below_xy])

print("Converting database.")
json_db = list()
for key in sorted(database.keys()):
    (t1, t2, dx, dy) = key
    entry = dict()
    entry["tile_types"] = [t1, t2]
    entry["grid_deltas"] = [dx, dy]
    entry["wire_pairs"] = list(sorted(database[key]))
    if len(entry["wire_pairs"]):
        json_db.append(entry)

print("Writing tileconn.json.")
with open("tileconn.json", "w") as f:
    print(json.dumps(json_db, sort_keys=True, indent="\t"), file=f)

