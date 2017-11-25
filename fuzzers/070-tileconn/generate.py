#!/usr/bin/env python3

import os, sys, json, re

database = dict()

print("Loading %s grid." % os.getenv("XRAY_DATABASE"))
with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")), "r") as f:
    grid = json.load(f)

print("Loading tilepairs.txt.")
with open("tilepairs.txt") as f:
    for line in f:
        w1, w2 = line.split()
        t1, w1 = w1.split("/")
        t2, w2 = w2.split("/")

        t1_type = grid["tiles"][t1]["type"]
        t1_grid_x = grid["tiles"][t1]["grid_x"]
        t1_grid_y = grid["tiles"][t1]["grid_y"]

        t2_type = grid["tiles"][t2]["type"]
        t2_grid_x = grid["tiles"][t2]["grid_x"]
        t2_grid_y = grid["tiles"][t2]["grid_y"]

        if (t1_grid_x < t2_grid_x) or ((t1_grid_x == t2_grid_x) and (t1_grid_y < t2_grid_y)):
            key = (t1_type, t2_type, t2_grid_x-t1_grid_x, t2_grid_y-t1_grid_y)
            if key not in database:
                database[key] = set()
            database[key].add((w1, w2))
        else:
            key = (t2_type, t1_type, t1_grid_x-t2_grid_x, t1_grid_y-t2_grid_y)
            if key not in database:
                database[key] = set()
            database[key].add((w2, w1))

print("Converting database.")
json_db = list()
for key in sorted(database.keys()):
    (t1, t2, dx, dy) = key
    entry = dict()
    entry["tile_types"] = [t1, t2]
    entry["grid_deltas"] = [dx, dy]
    entry["wire_pairs"] = list(sorted(database[key]))
    json_db.append(entry)

print("Writing tileconn.json.")
with open("tileconn.json", "w") as f:
    print(json.dumps(json_db, sort_keys=True, indent="\t"), file=f)

