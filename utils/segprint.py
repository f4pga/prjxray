#!/usr/bin/env python3

import sys, os, json, re

# print("Loading %s grid." % os.getenv("XRAY_DATABASE"))
with open("%s/../database/%s/tilegrid.json" % (os.path.dirname(sys.modules[__name__].__file__), os.getenv("XRAY_DATABASE")), "r") as f:
    grid = json.load(f)

bitdata = dict()

# print("Loading %s." % sys.argv[1])
with open(sys.argv[1], "r") as f:
    for line in f:
        line = line.split("_")
        frame = int(line[1], 16)
        wordidx = int(line[2], 10)
        bitidx = int(line[3], 10)

        if frame not in bitdata:
            bitdata[frame] = dict()

        if wordidx not in bitdata[frame]:
            bitdata[frame][wordidx] = set()

        bitdata[frame][wordidx].add(bitidx)

for arg in sys.argv[2:]:
    if arg in grid["tiles"]:
        segname = grid["tiles"][arg]["segment"]
    else:
        segname = arg

    print()
    print("seg %s" % segname)

    seginfo = grid["segments"][segname]

    baseframe = int(seginfo["baseaddr"][0], 16)
    basewordidx = int(seginfo["baseaddr"][1])
    numframes = int(seginfo["frames"])
    numwords = int(seginfo["words"])

    for frame in range(baseframe, baseframe+numframes):
        if frame not in bitdata:
            continue
        for wordidx in range(basewordidx, basewordidx+numwords):
            if wordidx not in bitdata[frame]:
                continue
            for bitidx in bitdata[frame][wordidx]:
                print("bit %02d_%02d" % (frame - baseframe, 32*(wordidx - basewordidx) + bitidx))

