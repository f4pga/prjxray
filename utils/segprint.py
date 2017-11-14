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

def handle_segment(segname):
    if ":" in segname:
        seg1, seg2 = segname.split(":")

        if seg1 in grid["tiles"]:
            seg1 = grid["tiles"][seg1]["segment"]

        if seg2 in grid["tiles"]:
            seg2 = grid["tiles"][seg2]["segment"]

        seginfo1 = grid["segments"][seg1]
        seginfo2 = grid["segments"][seg2]

        frame1 = int(seginfo1["baseaddr"][0], 16)
        word1 = int(seginfo1["baseaddr"][1])

        frame2 = int(seginfo2["baseaddr"][0], 16)
        word2 = int(seginfo2["baseaddr"][1])

        if frame1 > frame2:
            frame1, frame2 = frame2, frame1

        if word1 > word2:
            word1, word2 = word2, word1

        segs = list()

        for seg, seginfo in sorted(grid["segments"].items()):
            frame = int(seginfo["baseaddr"][0], 16)
            word = int(seginfo["baseaddr"][1])
            if frame1 <= frame <= frame2 and word1 <= word <= word2:
                segs.append((frame, word, seg))

        for _, _, seg in sorted(segs):
            handle_segment(seg)
        return

    if segname in grid["tiles"]:
        segname = grid["tiles"][segname]["segment"]

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

for arg in sys.argv[2:]:
    handle_segment(arg)

