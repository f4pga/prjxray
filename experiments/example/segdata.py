#!/usr/bin/env python3

import os, json, re

#################################################
# Loading Raw Source Data

grid = None
bits = dict()
luts = dict()
carry = dict()

print("Loading grid.")
with open("../../../gridinfo/grid-%s-db.json" % os.getenv("XRAY_PART"), "r") as f:
    grid = json.load(f)

print("Loading bits.")
with open("design.bits", "r") as f:
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

print("Loading lut data.")
with open("lutdata.txt", "r") as f:
    for line in f:
        line = line.split()
        site = line[0]
        bel = line[1]
        init = int(line[2][4:], 16)

        if site not in luts:
            luts[site] = dict()

        for i in range(64):
            bitname = "%s.INIT[%02d]" % (bel, i)
            luts[site][bitname] = ((init >> i) & 1) != 0

print("Loading carry data.")
with open("carrydata.txt", "r") as f:
    for line in f:
        line = line.split()
        assert line[0] not in carry
        carry[line[0]] = dict()
        for i, n in enumerate("CYINIT:ZRO:ONE:AX:CIN DI0:AX:O5 DI1:AX:O5 DI2:AX:O5 DI3:AX:O5".split()):
            n = n.split(":")
            for k in n[1:]:
                carry[line[0]]["CARRY_%s_MUX_%s" % (n[0], k)] = line[1+i].upper() == k


#################################################
# Group per Segment

print("Compile segment data.")

segments = dict()

for tilename, tiledata in grid["tiles"].items():
    found_data = False
    for site in tiledata["sites"]:
        if site in luts:
            found_data = True

    if not found_data:
        continue

    segname = "%s_%02x" % (tiledata["cfgcol"]["BASE_FRAMEID"][2:], min(tiledata["cfgcol"]["WORDS"]))

    if not segname in segments:
        segments[segname] = { "bits": list(), "tags": dict() }

    for site in tiledata["sites"]:
        if site not in luts and site not in carry:
            continue

        if re.match(r"SLICE_X[0-9]*[02468]Y", site):
            sitekey = "SLICE_X0"
        elif re.match(r"SLICE_X[0-9]*[13579]Y", site):
            sitekey = "SLICE_X1"
        else:
            assert 0

        if site in luts:
            for name, value in luts[site].items():
                tile_type = tiledata["props"]["TYPE"]

                # LUT init bits are in the same position for all CLBL[LM]_[LR] tiles
                if re.match("^CLBL[LM]_[LR]", tile_type) and "LUT.INIT" in name:
                    tile_type = "CLBLX_X"

                segments[segname]["tags"]["%s.%s.%s" % (tile_type, sitekey, name)] = value

        if site in carry:
            for name, value in carry[site].items():
                tile_type = tiledata["props"]["TYPE"]
                segments[segname]["tags"]["%s.%s.%s" % (tile_type, sitekey, name)] = value

    base_frame = int(tiledata["cfgcol"]["BASE_FRAMEID"][2:], 16)
    for wordidx in tiledata["cfgcol"]["WORDS"]:
        if base_frame not in bits:
            continue
        if wordidx not in bits[base_frame]:
            continue
        for bit_frame, bit_wordidx, bit_bitidx in bits[base_frame][wordidx]:
            segments[segname]["bits"].append("%02x_%02x_%02x" % (bit_frame - base_frame, bit_wordidx - min(tiledata["cfgcol"]["WORDS"]), bit_bitidx))

    segments[segname]["bits"].sort()


#################################################
# Print

print("Write segment data.")

with open("segdata.txt", "w") as f:
    for segname, segdata in sorted(segments.items()):
        print("seg %s" % segname, file=f)
        for bitname in sorted(segdata["bits"]):
            print("bit %s" % bitname, file=f)
        for tagname, tagval in sorted(segdata["tags"].items()):
            print("tag %s %d" % (tagname, tagval), file=f)

