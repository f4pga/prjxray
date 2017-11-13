#!/usr/bin/env python3

import os, sys, json, re


class UnionFind:
    def __init__(self):
        self.parents = dict()

    def make(self, value):
        if value not in self.parents:
            self.parents[value] = value

    def find(self, value):
        self.make(value)
        if self.parents[value] != value:
            retval = self.find(self.parents[value])
            self.parents[value] = retval
        return self.parents[value]

    def union(self, v1, v2):
        a = self.find(v1)
        b = self.find(v2)
        if a != b:
            self.parents[a] = b


#################################################
# Loading Raw Source Data

grid = None
segbits = dict()
segbits_r = dict()
segframes = dict()
routebits = dict()

print("Loading tilegrid.")
with open("../database/%s/tilegrid.json" % os.getenv("XRAY_DATABASE"), "r") as f:
    grid = json.load(f)

for segname, segdata in grid["segments"].items():
    segtype = segdata["type"].lower()

    if segtype not in segbits:
        segbits[segtype] = dict()
        segbits_r[segtype] = dict()
        routebits[segtype] = dict()
        segframes[segtype] = segdata["frames"]

        print("Loading %s segbits." % segtype)
        with open("../database/%s/seg_%s.segbits" % (os.getenv("XRAY_DATABASE"), segtype)) as f:
            for line in f:
                bit_name, bit_pos = line.split()
                segbits[segtype][bit_name] = bit_pos
                segbits_r[segtype][bit_pos] = bit_name

        print("Loading %s_int segbits." % segtype)
        with open("../database/%s/seg_%s.segbits" % (os.getenv("XRAY_DATABASE"), segtype.replace("_", "_int_"))) as f:
            for line in f:
                bit_name, *bit_pos = line.split()
                for bit in bit_pos:
                    if bit not in routebits[segtype]:
                        routebits[segtype][bit] = set()
                    routebits[segtype][bit].add(bit_name)


#################################################
# Create Tilegrid Page

grid_range = None
grid_map = dict()

print("Writing %s/index.html." % os.getenv("XRAY_DATABASE"))
os.makedirs(os.getenv("XRAY_DATABASE"), exist_ok=True)
with open("%s/index.html" % os.getenv("XRAY_DATABASE"), "w") as f:
    print("<html><title>X-Ray %s Database</title><body>" % os.getenv("XRAY_DATABASE").upper(), file=f)
    print("<h3>X-Ray %s Database</h3>" % os.getenv("XRAY_DATABASE").upper(), file=f)

    print("<p><b>Part: %s<br/>ROI: %s<br/>ROI Frames: %s</b></p>" % (os.getenv("XRAY_PART"), os.getenv("XRAY_ROI"), os.getenv("XRAY_ROI_FRAMES")), file=f)

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

    print("<table border>", file=f)

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

            print("<td bgcolor=\"%s\" align=\"center\" title=\"%s\"><span style=\"font-size:10px\">" % (bgcolor, "\n".join(title)), file=f)
            if "segment" in tiledata:
                segtype = segdata["type"].lower()
                print("<a style=\"text-decoration: none; color: black\" href=\"seg_%s.html\">%s</a></span></td>" %
                        (segtype, tilename.replace("_X", "<br/>X")), file=f)
            else:
                print("%s</span></td>" % tilename.replace("_X", "<br/>X"), file=f)

        print("</tr>", file=f)

    print("</table>", file=f)
    print("</body></html>", file=f)


#################################################
# Create Segment Pages

for segtype in segbits.keys():
    print("Writing %s/seg_%s.html." % (os.getenv("XRAY_DATABASE"), segtype))
    with open("%s/seg_%s.html" % (os.getenv("XRAY_DATABASE"), segtype), "w") as f:
        print("<html><title>X-Ray %s Database: %s</title><body>" % (os.getenv("XRAY_DATABASE").upper(), segtype.upper()), file=f)
        print("<h3>X-Ray %s Database: %s</h3>" % (os.getenv("XRAY_DATABASE").upper(), segtype.upper()), file=f)
        print("<table border>", file=f)

        print("<tr>", file=f)
        print("<th width=\"30\"></th>", file=f)
        for frameidx in range(segframes[segtype]):
            print("<th width=\"30\"><span style=\"font-size:10px\">%d</span></th>" % frameidx, file=f)
        print("</tr>", file=f)

        for bitidx in range(63, -1, -1):
            print("<tr>", file=f)
            print("<th align=\"right\"><span style=\"font-size:10px\">%d</span></th>" % bitidx, file=f)
            for frameidx in range(segframes[segtype]):
                bit_pos = "%02d_%02d" % (frameidx, bitidx)
                bit_name = segbits_r[segtype][bit_pos] if bit_pos in segbits_r[segtype] else None

                label = "&nbsp;"
                title = [bit_pos]
                bgcolor = "#aaaaaa"

                if bit_name is not None:
                    bgcolor = "#ff0000"
                    title.append(bit_name)

                    if "LUT.INIT" in bit_name:
                        bgcolor = "#ffffaa"
                        m = re.search(r"(.)LUT.INIT\[(..)\]", bit_name)
                        label = m.group(1) + m.group(2)

                    if re.search(r"\.[ABCD]5?FF\.", bit_name):
                        bgcolor = "#aaffaa"
                        m = re.search(r"\.([ABCD]5?)FF\.([A-Z]+)", bit_name)
                        if m.group(2) == "ZINI":
                            label = m.group(1) + "Z"
                        else:
                            label = m.group(1) + "?"

                    if re.search(r"\.[ABCD]5?FF\.", bit_name):
                        bgcolor = "#aaffaa"
                        m = re.search(r"\.([ABCD]5?)FF\.([A-Z]+)", bit_name)
                        if m.group(2) == "ZINI":
                            label = m.group(1) + "Z"
                        else:
                            label = m.group(1) + "?"

                    if re.search(r"\.[ABCD]LUT5$", bit_name):
                        bgcolor = "#cccc88"
                        label = bit_name[-5] + "5"

                elif bit_pos in routebits[segtype]:
                        title += list(routebits[segtype][bit_pos])
                        bgcolor = "#6666cc"
                        label = "R"

                print("<td bgcolor=\"%s\" title=\"%s\"><span style=\"font-size:10px\">%s</span></td>" % (bgcolor, "\n".join(title), label), file=f)
            print("</tr>", file=f)
        print("</table>", file=f)


        bits_by_prefix = dict()

        for bit_name, bit_pos in segbits[segtype].items():
            prefix = ".".join(bit_name.split(".")[0:-1])

            if prefix not in bits_by_prefix:
                bits_by_prefix[prefix] = set()

            bits_by_prefix[prefix].add((bit_name, bit_pos))

        for prefix, bits in sorted(bits_by_prefix.items()):
            print("<p/>", file=f)
            print("<h4>%s</h4>" % prefix, file=f)
            print("<table cellspacing=0>", file=f)
            print("<tr><th width=\"400\" align=\"left\">Bit Name</th><th>Position</th></tr>", file=f)

            trstyle = ""
            for bit_name, bit_pos in sorted(bits):
                trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
                print("<tr%s><td>%s</td><td>%s</td></tr>" % (trstyle, bit_name, bit_pos), file=f)

            print("</table>", file=f)

        ruf = UnionFind()

        for bit, pips in routebits[segtype].items():
            for pip in pips:
                grp = pip.split('.')[1]
                ruf.union(grp, bit)

        rgroups = dict()
        rgroup_names = dict()

        for bit, pips in routebits[segtype].items():
            for pip in pips:
                grp_name = pip.split('.')[1]
                grp = ruf.find(grp_name)
                if grp not in rgroup_names:
                    rgroup_names[grp] = set()
                rgroup_names[grp].add(grp_name)
                if grp not in rgroups:
                    rgroups[grp] = dict()
                if pip not in rgroups[grp]:
                    rgroups[grp][pip] = set()
                rgroups[grp][pip].add(bit)

        for grp, gdata in sorted(rgroups.items()):
            print("<p/>", file=f)
            print("<h4>%s</h4>" % ", ".join(sorted(rgroup_names[grp])), file=f)
            print("<table cellspacing=0>", file=f)
            print("<tr><th width=\"400\" align=\"left\">PIP</th>", file=f)

            grp_bits = set()
            for pip, bits in gdata.items():
                grp_bits |= bits
            grp_bits = sorted(grp_bits)

            for bit in grp_bits:
                print("<th>&nbsp;%s&nbsp;</th>" % bit, file=f)
            print("</tr>", file=f)

            lines = list()
            for pip, bits in sorted(gdata.items()):
                line = " --><td>%s</td>" % (pip)
                for bit in grp_bits:
                    c = "1" if bit in bits else "-"
                    line = "%s%s<td align=\"center\">%s</td>" % (c, line, c)
                lines.append(line)

            trstyle = ""
            for line in sorted(lines):
                trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
                print("<tr%s><!-- %s</tr>" % (trstyle, line), file=f)

            print("</table>", file=f)

        print("</body></html>", file=f)

