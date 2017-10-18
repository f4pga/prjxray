#!/usr/bin/env python3

import os, sys, json, re


#################################################
# Loading Raw Source Data

grid = None
bits = dict()
data = dict()

print("Loading grid.")
with open("../../../database/%s/tilegrid.json" % os.getenv("XRAY_DATABASE"), "r") as f:
    grid = json.load(f)

print("Loading bits.")
with open("design_%s.bits" % sys.argv[1], "r") as f:
    for line in f:
        line = line.split("_")
        bit_frame = int(line[1], 16)
        bit_wordidx = int(line[2], 16)
        bit_bitidx = int(line[3], 16)
        base_frame = bit_frame & ~0x7f

        if base_frame not in bits:
            bits[base_frame] = dict()

        if bit_wordidx not in bits[base_frame]:
            bits[base_frame][bit_wordidx] = set()

        bits[base_frame][bit_wordidx].add((bit_frame, bit_wordidx, bit_bitidx))

print("Loading text data.")
with open("design_%s.txt" % sys.argv[1], "r") as f:
    for line in f:
        line = line.split()
        site = line[0]
        bel = line[1]
        init = int(line[2][3])
        cinv = int(line[3][3])
        dinv = int(line[4][3])
        rinv = int(line[5][3])

        if site not in data:
            data[site] = dict()

        data[site]["%s.ZINI" % bel] = 1-init
        # data[site]["%s.CINV" % bel] = cinv
        # data[site]["%s.DINV" % bel] = dinv
        # data[site]["%s.RINV" % bel] = rinv


#################################################
# Group per Segment

print("Compile segment data.")

segments_by_type = dict()

for tilename, tiledata in grid["tiles"].items():
    if "segment" not in tiledata:
        continue

    segdata = grid["segments"][tiledata["segment"]]

    if segdata["type"] not in segments_by_type:
        segments_by_type[segdata["type"]] = dict()
    segments = segments_by_type[segdata["type"]]

    tile_type = tiledata["type"]
    segname = "%s_%02x" % (segdata["baseaddr"][0][2:], segdata["baseaddr"][1])

    if not segname in segments:
        segments[segname] = { "bits": list(), "tags": dict() }

    for site in tiledata["sites"]:
        if site not in data:
            continue

        if re.match(r"SLICE_X[0-9]*[02468]Y", site):
            sitekey = "SLICE_X0"
        elif re.match(r"SLICE_X[0-9]*[13579]Y", site):
            sitekey = "SLICE_X1"
        else:
            assert 0

        for name, value in data[site].items():
            tag = "%s.%s.%s" % (re.sub("_[LR]$", "", tile_type), sitekey, name)
            tag = tag.replace("SLICE_X0.SLICEM", "SLICEM_X0")
            tag = tag.replace("SLICE_X1.SLICEM", "SLICEM_X1")
            tag = tag.replace("SLICE_X0.SLICEL", "SLICEL_X0")
            tag = tag.replace("SLICE_X1.SLICEL", "SLICEL_X1")
            segments[segname]["tags"][tag] = value

    base_frame = int(segdata["baseaddr"][0][2:], 16)
    for wordidx in range(segdata["baseaddr"][1], segdata["baseaddr"][1]+2):
        if base_frame not in bits:
            continue
        if wordidx not in bits[base_frame]:
            continue
        for bit_frame, bit_wordidx, bit_bitidx in bits[base_frame][wordidx]:
            segments[segname]["bits"].append("%02x_%02x_%02x" % (bit_frame - base_frame, bit_wordidx - segdata["baseaddr"][1], bit_bitidx))

    segments[segname]["bits"].sort()


#################################################
# Print

print("Write segment data.")

for segtype in segments_by_type.keys():
    with open("segdata_%s_%s.txt" % (segtype, sys.argv[1]), "w") as f:
        segments = segments_by_type[segtype]
        for segname, segdata in sorted(segments.items()):
            print("seg %s" % segname, file=f)
            for bitname in sorted(segdata["bits"]):
                print("bit %s" % bitname, file=f)
            for tagname, tagval in sorted(segdata["tags"].items()):
                print("tag %s %d" % (tagname, tagval), file=f)

