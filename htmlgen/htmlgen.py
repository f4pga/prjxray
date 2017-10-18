#!/usr/bin/env python3

import os, sys, json, re


#################################################
# Loading Raw Source Data

grid = None
segbits = dict()
segbits_r = dict()
segframes = dict()

print("Loading tilegrid.")
with open("../database/%s/tilegrid.json" % os.getenv("XRAY_DATABASE"), "r") as f:
    grid = json.load(f)

for segname, segdata in grid["segments"].items():
    segtype = segdata["type"].lower()
    segtype = re.sub(r"_[lr]$", "", segtype)

    if segtype not in segbits:
        segbits[segtype] = dict()
        segbits_r[segtype] = dict()
        segframes[segtype] = 36

        print("Loading %s segbits." % segtype)
        with open("../database/%s/seg_%s.segbits" % (os.getenv("XRAY_DATABASE"), segtype)) as f:
            for line in f:
                bit_name, bit_pos = line.split()
                segbits[segtype][bit_name] = bit_pos
                segbits_r[segtype][bit_pos] = bit_name


#################################################
# Create Tilegrid Page

grid_range = None
grid_map = dict()

print("Writing %s/index.html." % os.getenv("XRAY_DATABASE"))
os.makedirs(os.getenv("XRAY_DATABASE"), exist_ok=True)
with open("%s/index.html" % os.getenv("XRAY_DATABASE"), "w") as f:
    print("<html><title>X-Ray %s Database</title><body>" % os.getenv("XRAY_DATABASE").upper(), file=f)

    for tilename, tiledata in grid["tiles"].items():
        grid_x = tiledata["grid_x"]
        grid_y = tiledata["grid_y"]
        grid_map[(grid_x, grid_y)] = tilename

        if grid_range is None:
            grid_range = [grid_x, grid_y, grid_x, grid_y]
        else:
            grid_range[0] = min(grid_range[0], grid_x)
            grid_range[1] = min(grid_range[1], grid_y)
            grid_range[2] = max(grid_range[2], grid_x)
            grid_range[3] = max(grid_range[3], grid_y)

    print("<table border>", file =f)

    for grid_y in range(grid_range[1], grid_range[3]+1):
        print("<tr>", file=f)

        for grid_x in range(grid_range[0], grid_range[2]+1):
            tilename = grid_map[(grid_x, grid_y)]
            tiledata = grid["tiles"][tilename]

            bgcolor = "#aaaaaa"
            if tiledata["type"] in ["INT_L", "INT_R"]: bgcolor="#aaaaff"
            if tiledata["type"] in ["CLBLL_L", "CLBLL_R"]: bgcolor="#ffffaa"
            if tiledata["type"] in ["CLBLM_L", "CLBLM_R"]: bgcolor="#ffaaaa"

            title = [tilename]
            
            if "segment" in tiledata:
                segdata = grid["segments"][tiledata["segment"]]
                title.append(tiledata["segment"])

            title.append("GRID_POSITION: %d %d" % (grid_x, grid_y))

            if "sites" in tiledata:
                for sitename, sitetype in tiledata["sites"].items():
                    title.append("%s site: %s" % (sitetype, sitename))

            if "segment" in tiledata:
                title.append("Baseaddr: %s %d" % tuple(segdata["baseaddr"]))

            print("<td bgcolor=\"%s\" title=\"%s\">" % (bgcolor, "\n".join(title)), file=f)
            if "segment" in tiledata:
                segtype = segdata["type"].lower()
                segtype = re.sub(r"_[lr]$", "", segtype)
                print("<center><small><a href=\"seg_%s.html\">%s</a></small></center></td>" %
                        (segtype, tilename.replace("_X", "<br/>X")), file=f)
            else:
                print("<center><small>%s</small></center></td>" % tilename.replace("_X", "<br/>X"), file=f)

        print("</tr>", file=f)

    print("</table>", file =f)
    print("</body></html>", file=f)


#################################################
# Create Segment Pages

for segtype in segbits.keys():
    print("Writing %s/seg_%s.html." % (os.getenv("XRAY_DATABASE"), segtype))
    with open("%s/seg_%s.html" % (os.getenv("XRAY_DATABASE"), segtype), "w") as f:
        print("<html><title>X-Ray %s Database: %s</title><body>" % (os.getenv("XRAY_DATABASE").upper(), segtype.upper()), file=f)
        print("<table border>", file =f)

        print("<tr>", file =f)
        print("<th width=\"50\"></th>", file =f)
        for frameidx in range(segframes[segtype]):
            print("<th width=\"50\">%d</th>" % frameidx, file =f)
        print("</tr>", file =f)

        for bitidx in range(63, -1, -1):
            print("<tr>", file =f)
            print("<th align=\"right\">%d</th>" % bitidx, file =f)
            for frameidx in range(segframes[segtype]):
                bit_pos = "%02x_%02x_%02x" % (frameidx, bitidx // 32, bitidx % 32)
                bit_name = segbits_r[segtype][bit_pos] if bit_pos in segbits_r[segtype] else None

                label = "&nbsp;"
                title = [bit_pos]
                bgcolor = "#aaaaaa"

                if bit_name is not None:
                    bgcolor = "#ff0000"
                    title.append(bit_name)

                    if "LUT.INIT" in bit_name:
                        bgcolor = "#ffffaa"
                        m = re.search(r"(.)6LUT.INIT\[(..)\]", bit_name)
                        label = m.group(1) + m.group(2)

                print("<td bgcolor=\"%s\" title=\"%s\">%s</td>" % (bgcolor, "\n".join(title), label), file=f)
            print("</tr>", file =f)

        print("</table>", file =f)
        print("</body></html>", file=f)

