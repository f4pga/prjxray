#!/usr/bin/env python3

import os, sys, json, re
from io import StringIO

import argparse

parser = argparse.ArgumentParser(
    description="Generate a pretty HTML version of the documentation.")
parser.add_argument(
    '--output', default=os.path.join(os.path.curdir, 'html'),
    help='Put the generated files in this directory (default current dir).')
parser.add_argument(
    '--settings', default=None,
    help='Read the settings from file (default to environment).')

args = parser.parse_args()

if args.settings:
    settings_filename = args.settings

    settings = {
        'XRAY_DATABASE_DIR': os.path.abspath(
            os.path.join(os.path.dirname(settings_filename), '..')),
    }
    with open(settings_filename) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("export "):
                continue
            key, value = line[7:].split('=', 1)
            settings[key] = value[1:-1]

    def get_setting(name):
        return settings[name]
else:
    def get_setting(name):
        return os.getenv(name)

db_dir = os.path.join(get_setting("XRAY_DATABASE_DIR"), get_setting("XRAY_DATABASE"))
def db_open(fn):
    filename = os.path.join(db_dir, fn)
    if not os.path.exists(filename):
        return StringIO("")
    return open(os.path.join(db_dir, fn))

def out_open(fn):
    out_dir = os.path.join(args.output, get_setting("XRAY_DATABASE"))
    os.makedirs(out_dir, exist_ok=True)
    fp = os.path.join(out_dir, fn)
    print("Writing %s" % fp)
    return open(fp, "w")

clb_bitgroups_db = [
    # copy&paste from zero_db in dbfixup.py
    "00_21 00_22 00_26 01_28|00_25 01_20 01_21 01_24",
    "00_23 00_30 01_22 01_25|00_27 00_29 01_26 01_29",
    "01_12 01_14 01_16 01_18|00_10 00_11 01_09 01_10",
    "00_13 01_17 00_15 00_17|00_18 00_19 01_13 00_14",
    "00_34 00_38 01_33 01_37|00_35 00_39 01_38 01_40",
    "00_33 00_41 01_32 01_34|00_37 00_42 01_36 01_41",

    # other manual groupings for individual bits
    "00_02 00_05 00_09 01_04|00_07 01_05 01_06",
    "00_01 00_06 01_00 01_08|00_03 01_01 01_02",
    "00_59 01_54 01_58 01_61|00_57 00_58 01_56",
    "00_55 00_63 01_57 01_62|00_61 00_62 01_60",
    "00_43 00_47 00_50 00_53 00_54 01_42|00_51 01_50 01_52",
    "00_49 01_44 01_45 01_48 01_49 01_53|00_45 00_46 01_46",
]

hclk_bitgroups_db = [
    # manual groupings
    "03_14 03_15 04_14 04_15|00_15 00_16 01_14 01_15",
    "02_16 03_16 04_16 05_16|02_14 02_15 05_14 05_15",
    "02_18 02_19 05_18 05_19|00_17 00_18 01_16 01_17",
    "03_18 03_19 04_18 04_19|02_17 03_17 04_17 05_17",
    "02_20 02_21 05_20 05_21|02_22 03_22 04_22 05_22",
    "02_29 03_29 04_29 05_29|03_30 03_31 04_30 04_31",
    "02_26 02_27 05_26 05_27|02_28 03_28 04_28 05_28",
    "02_23 03_23 04_23 05_23|03_24 03_25 04_24 04_25",
]

# groupings for SNWE bits in frames 2..7
for i in range(0, 64, 4):
    clb_bitgroups_db.append("02_%02d 03_%02d 05_%02d 06_%02d 07_%02d|05_%02d 03_%02d 04_%02d 04_%02d" %
            (i+1, i, i, i, i+1, i+3, i+1, i+1, i+2))
    clb_bitgroups_db.append("02_%02d 04_%02d 05_%02d 05_%02d 06_%02d|02_%02d 03_%02d 04_%02d 07_%02d" %
            (i+2, i, i+1, i+2, i+2, i+3, i+2, i+3, i+3))

clb_left_bits = set()
clb_right_bits = set()

for entry in clb_bitgroups_db:
    a, b = entry.split("|")
    for bit in a.split():
        clb_left_bits.add(bit)
    for bit in b.split():
        clb_right_bits.add(bit)

hclk_left_bits = set()
hclk_right_bits = set()

for entry in hclk_bitgroups_db:
    a, b = entry.split("|")
    for bit in a.split():
        hclk_left_bits.add(bit)
    for bit in b.split():
        hclk_right_bits.add(bit)

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
segtiles = dict()
routebits = dict()
routezbits = dict()
maskbits = dict()


print("Loading tilegrid.")
with db_open("tilegrid.json") as f:
    data = f.read()
    if not data:
        grid = {
            "segments": {},
            "tiles": {
                "NULL": {
                    "grid_x": 0,
                    "grid_y":0,
                    "type":"NULL",
                }
            }
        }
    else:
        grid = json.loads(data)

for segname, segdata in grid["segments"].items():
    segtype = segdata["type"].lower()

    if segtype not in segbits:
        segbits[segtype] = dict()
        segbits_r[segtype] = dict()
        routebits[segtype] = dict()
        routezbits[segtype] = dict()
        maskbits[segtype] = set()
        segframes[segtype] = segdata["frames"]

        segtiles[segtype] = set()
        for t in segdata["tiles"]:
            segtiles[segtype].add(grid["tiles"][t]["type"])

        def add_pip_bits(line):
            bit_name, *bit_pos = line.split()
            for bit in bit_pos:
                if bit[0] == "!":
                    if bit[1:] not in routezbits[segtype]:
                        routezbits[segtype][bit[1:]] = set()
                    routezbits[segtype][bit[1:]].add(bit_name)
                else:
                    if bit not in routebits[segtype]:
                        routebits[segtype][bit] = set()
                    routebits[segtype][bit].add(bit_name)

        def add_single_bit(line):
            bit_name, bit_pos = line.split()
            assert bit_pos[0] != "!"
            segbits[segtype][bit_name] = bit_pos
            segbits_r[segtype][bit_pos] = bit_name

        if segtype not in ["hclk_l", "hclk_r"]:
            print("Loading %s segbits." % segtype)
            with db_open("segbits_%s.db" % segtype) as f:
                for line in f:
                    if re.search(r"(\.[ABCD]MUX\.)|(\.PRECYINIT\.)", line):
                        add_pip_bits(line)
                    else:
                        add_single_bit(line)

        print("Loading %s segbits." % re.sub("clbl[lm]", "int", segtype))
        with db_open("segbits_%s.db" % re.sub("clbl[lm]", "int", segtype)) as f:
            for line in f:
                if segtype in ["hclk_l", "hclk_r"] and ".ENABLE_BUFFER." in line:
                    add_single_bit(line)
                else:
                    add_pip_bits(line)

        print("Loading %s maskbits." % segtype)
        with db_open("mask_%s.db" % segtype) as f:
            for line in f:
                _, bit = line.split()
                maskbits[segtype].add(bit)


#################################################
# Create Tilegrid Page

grid_range = None
grid_map = dict()

with out_open("index.html") as f:
    print("<html><title>X-Ray %s Database</title><body>" % get_setting("XRAY_DATABASE").upper(), file=f)
    print("<h3>X-Ray %s Database</h3>" % get_setting("XRAY_DATABASE").upper(), file=f)

    print("<p><b>Part: %s<br/>ROI: %s<br/>ROI Frames: %s</b></p>" % (get_setting("XRAY_PART"), get_setting("XRAY_ROI"), get_setting("XRAY_ROI_FRAMES")), file=f)

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
            segdata = None

            bgcolor = "#aaaaaa"
            if tiledata["type"] in ["INT_L", "INT_R"]: bgcolor="#aaaaff"
            if tiledata["type"] in ["CLBLL_L", "CLBLL_R"]: bgcolor="#ffffaa"
            if tiledata["type"] in ["CLBLM_L", "CLBLM_R"]: bgcolor="#ffaaaa"
            if tiledata["type"] in ["HCLK_L", "HCLK_R"]: bgcolor="#aaffaa"

            title = [tilename]

            if "segment" in tiledata:
                segdata = grid["segments"][tiledata["segment"]]
                title.append(tiledata["segment"])

            title.append("GRID_POSITION: %d %d" % (grid_x, grid_y))

            if "sites" in tiledata:
                for sitename, sitetype in tiledata["sites"].items():
                    title.append("%s site: %s" % (sitetype, sitename))

            if "segment" in tiledata:
                if "baseaddr" in segdata:
                    title.append("Baseaddr: %s %d" % tuple(segdata["baseaddr"]))
                else:
                    print("Warning: no baseaddr in segment %s (via tile %s)." % (tiledata["segment"], tilename))

            print("<td bgcolor=\"%s\" align=\"center\" title=\"%s\"><span style=\"font-size:10px\">" % (bgcolor, "\n".join(title)), file=f)
            if "segment" in tiledata:
                segtype = segdata["type"].lower()
                print("<a style=\"text-decoration: none; color: black\" href=\"seg_%s.html\">%s</a></span></td>" %
                        (segtype, tilename.replace("_X", "<br/>X")), file=f)
            else:
                print("%s</span></td>" % tilename.replace("_X", "<br/>X").replace("B_TERM", "B<br/>TERM"), file=f)

        print("</tr>", file=f)

    print("</table>", file=f)
    print("</body></html>", file=f)


#################################################
# Create Segment Pages

for segtype in sorted(segbits.keys()):
    with out_open("seg_%s.html" % segtype) as f:
        print("<html><title>X-Ray %s Database: %s</title><body>" % (get_setting("XRAY_DATABASE").upper(), segtype.upper()), file=f)
        if segtype in ["hclk_l", "hclk_r"]:
            print("<h3>X-Ray %s Database: %s Segment</h3>" % (get_setting("XRAY_DATABASE").upper(), segtype.upper()), file=f)
        else:
            print("<h3>X-Ray %s Database: %s Segment (%s Tile + %s Tile)</h3>" % (get_setting("XRAY_DATABASE").upper(), segtype.upper(),
                    segtype.upper(), re.sub("clbl[lm]", "int", segtype).upper()), file=f)

        print("""
<script><!--
var grp2bits = { };
var bit2grp = { }
var highlight_bits = [ ];
var highlight_cache = { };

function ome(bit) {
    // console.log("ome: " + bit);
    if (bit in bit2grp) {
        grp = bit2grp[bit];
        for (i in grp2bits[grp]) {
            b = grp2bits[grp][i];
            // console.log("  -> " + b);
            if (!(b in highlight_cache)) {
                el = document.getElementById("bit" + b);
                highlight_cache[b] = el.bgColor;
                el.bgColor = "#ffffff";
                highlight_bits.push(b);
            }
        }
    }
}

function oml() {
    // console.log("oml");
    for (i in highlight_bits) {
        b = highlight_bits[i];
        el = document.getElementById("bit" + b);
        el.bgColor = highlight_cache[b];
        delete highlight_cache[b];
        el.style.fontWeight = "normal";
    }
    highlight_bits.length = 0;
}
//--></script>
        """, file=f)

        print("<table border>", file=f)

        unused_bits = 0
        unknown_bits = 0
        known_bits = 0
        piptypes = dict()

        print("<tr>", file=f)
        print("<th width=\"30\"></th>", file=f)
        for frameidx in range(segframes[segtype]):
            print("<th width=\"30\"><span style=\"font-size:10px\">%d</span></th>" % frameidx, file=f)
        print("</tr>", file=f)

        for bitidx in range(31 if (segtype in ["hclk_l", "hclk_r"]) else 63, -1, -1):
            print("<tr>", file=f)
            print("<th align=\"right\"><span style=\"font-size:10px\">%d</span></th>" % bitidx, file=f)
            for frameidx in range(segframes[segtype]):
                bit_pos = "%02d_%02d" % (frameidx, bitidx)
                bit_name = segbits_r[segtype][bit_pos] if bit_pos in segbits_r[segtype] else None

                label = None
                title = [bit_pos]
                bgcolor = "#aaaaaa"

                if bit_pos not in maskbits[segtype]:
                    label = "&nbsp;"
                    bgcolor = "#444444"
                    title.append("UNUSED ?")

                if (segtype in ["hclk_l", "hclk_r"]) and bitidx < 13:
                    label = "ECC"
                    bgcolor = "#44aa44"

                if bit_name is not None:
                    bgcolor = "#ff0000"
                    title.append(bit_name)

                    if "LUT.INIT" in bit_name:
                        bgcolor = "#ffffaa"
                        m = re.search(r"(.)LUT.INIT\[(..)\]", bit_name)
                        label = m.group(1) + m.group(2)

                    m = re.search(r"\.([ABCD])LUT\.([A-Z]+)$", bit_name)
                    if m:
                        bgcolor = "#ffffaa"
                        if m.group(2) == "RAM":
                            label = m.group(1) + "LR"
                        elif m.group(2) == "SMALL":
                            label = m.group(1) + "LS"
                        elif m.group(2) == "SRL":
                            label = m.group(1) + "SR"
                        else:
                            bgcolor = "#ff0000"

                    m = re.search(r"\.([ABCD])LUT\.([A-Z]+)$", bit_name)
                    if m:
                        bgcolor = "#ffffaa"
                        if m.group(2) == "RAM":
                            label = m.group(1) + "LR"
                        elif m.group(2) == "SMALL":
                            label = m.group(1) + "LS"
                        elif m.group(2) == "SRL":
                            label = m.group(1) + "SR"
                        else:
                            bgcolor = "#ff0000"

                    m = re.search(r"\.([ABCD]5?)FF\.([A-Z]+(\.A|\.B)?)$", bit_name)
                    if m:
                        bgcolor = "#aaffaa"
                        if m.group(2) == "ZINI":
                            label = m.group(1) + "ZI"
                        elif m.group(2) == "ZRST":
                            label = m.group(1) + "ZR"
                        elif m.group(2) == "MUX.A":
                            label = m.group(1) + "MA"
                        elif m.group(2) == "MUX.B":
                            label = m.group(1) + "MB"
                        else:
                            bgcolor = "#ff0000"

                    m = re.search(r"\.([ABCD])DI1MUX\.", bit_name)
                    if m:
                        bgcolor = "#ffffaa"
                        label = m.group(1) + "DI1"

                    m = re.search(r"\.(WA[78])USED$", bit_name)
                    if m:
                        bgcolor = "#ffffaa"
                        label = m.group(1)

                    if ".WEMUX." in bit_name:
                        bgcolor = "#ffffaa"
                        label = "WE"

                    m = re.search(r"\.CARRY4\.([A-Z0-9]+)$", bit_name)
                    if m:
                        bgcolor = "#88cc00"
                        label = m.group(1)

                    if re.search(r"\.LATCH$", bit_name):
                        bgcolor = "#aaffaa"
                        label = "LAT"

                    if re.search(r"\.FFSYNC$", bit_name):
                        bgcolor = "#aaffaa"
                        label = "SYN"

                    if re.search(r"\.[ABCD]LUT5$", bit_name):
                        bgcolor = "#cccc88"
                        label = bit_name[-5] + "5"

                    if re.search(r"\.(CE|SR)USEDMUX$", bit_name):
                        bgcolor = "#ffaa00"
                        label = bit_name[-9:-7] + "M"

                    if re.search(r"\.CLKINV$", bit_name):
                        bgcolor = "#ffaa00"
                        label = "CLKI"

                    if ".ENABLE_BUFFER." in bit_name:
                        bgcolor = "#ffaa00"
                        label = "BUF"

                elif bit_pos in routebits[segtype]:
                        bgcolor = "#0000ff"
                        label = "R"
                        for bn in sorted(routebits[segtype][bit_pos]):
                            if re.match("^INT_[LR].[SNWE][SNWE]", bn):
                                bgcolor = "#aa88ff"
                                label = "SNWE"
                            elif re.match("^INT_[LR].IMUX", bn):
                                bgcolor = "#88aaff"
                                label = "IMUX"
                            elif re.match("^INT_[LR].BYP_ALT", bn):
                                bgcolor = "#7755ff"
                                label = "BALT"
                            elif re.match("^INT_[LR].FAN_ALT", bn):
                                bgcolor = "#4466bb"
                                label = "FALT"
                            elif re.match("^INT_[LR].[SNWE][RL]", bn):
                                bgcolor = "#4466bb"
                                label = "RL"
                            elif re.match("^INT_[LR].CLK", bn):
                                bgcolor = "#4466bb"
                                label = "CLK"
                            elif re.match("^INT_[LR].CTRL", bn):
                                bgcolor = "#7755ff"
                                label = "CTRL"
                            elif re.match("^INT_[LR].GFAN", bn):
                                bgcolor = "#7755ff"
                                label = "GFAN"
                            elif re.match("^INT_[LR].LVB", bn):
                                bgcolor = "#88aaff"
                                label = "LVB"
                            elif re.match("^INT_[LR].LV", bn):
                                bgcolor = "#88aaff"
                                label = "LV"
                            elif re.match("^INT_[LR].LH", bn):
                                bgcolor = "#4466bb"
                                label = "LH"
                            elif re.match("^CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]FF.DMUX", bn):
                                bgcolor = "#88aaff"
                                label = "DMX"
                            elif re.match("^CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]MUX", bn):
                                bgcolor = "#aa88ff"
                                label = "OMX"
                            elif re.match("^CLBL[LM]_[LR].SLICE[LM]_X[01].PRECYINIT", bn):
                                bgcolor = "#88aaff"
                                label = "CYI"
                            elif re.match("^HCLK_[LR]", bn) and "_B_BOT" in bn:
                                bgcolor = "#4466bb"
                                label = "BOT"
                            elif re.match("^HCLK_[LR]", bn) and "_B_TOP" in bn:
                                bgcolor = "#7755ff"
                                label = "TOP"
                            piptypes[bit_pos] = label
                            title.append(bn)

                if label is None:
                    label = "&nbsp;"
                    title.append("UNKNOWN")
                    onclick = ""
                else:
                    onclick = " onmousedown=\"location.href = '#b%s'\"" % bit_pos

                if bgcolor == "#aaaaaa":
                    unknown_bits += 1
                elif bgcolor == "#444444":
                    unused_bits += 1
                else:
                    known_bits += 1

                print("<td id=\"bit%s\" onmouseenter=\"ome('%s');\" onmouseleave=\"oml();\" bgcolor=\"%s\" align=\"center\" title=\"%s\"%s><span style=\"font-size:10px\">%s</span></td>" %
                        (bit_pos, bit_pos, bgcolor, "\n".join(title), onclick, label), file=f)
            print("</tr>", file=f)
        print("</table>", file=f)

        print("<div>", file=f)

        print("<h3>Segment Configuration Bits</h3>", file=f)

        if True:
            print("  unused: %d, unknown: %d, known: %d, total: %d, percentage: %.2f%% (%.2f%%)" % (
                    unused_bits, unknown_bits, known_bits, unused_bits + unknown_bits + known_bits,
                    100 * known_bits / (unknown_bits + unused_bits + known_bits),
                    100 * (known_bits + unused_bits) / (unknown_bits + unused_bits + known_bits)))

        bits_by_prefix = dict()

        for bit_name, bit_pos in segbits[segtype].items():
            prefix = ".".join(bit_name.split(".")[0:-1])

            if prefix not in bits_by_prefix:
                bits_by_prefix[prefix] = set()

            bits_by_prefix[prefix].add((bit_name, bit_pos))

        for prefix, bits in sorted(bits_by_prefix.items()):
            for bit_name, bit_pos in sorted(bits):
                print("<a id=\"b%s\"/>" % bit_pos, file=f)

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
        routebits_routezbits = list(routebits[segtype].items())
        routebits_routezbits += list(routezbits[segtype].items())

        for bit, pips in routebits_routezbits:
            for pip in pips:
                grp = ".".join(pip.split('.')[:-1])
                ruf.union(grp, bit)

        rgroups = dict()
        rgroup_names = dict()

        for bit, pips in routebits_routezbits:
            for pip in pips:
                grp_name = ".".join(pip.split('.')[:-1])
                grp = ruf.find(grp_name)
                if grp not in rgroup_names:
                    rgroup_names[grp] = set()
                rgroup_names[grp].add(grp_name)
                if grp not in rgroups:
                    rgroups[grp] = dict()
                if pip not in rgroups[grp]:
                    rgroups[grp][pip] = set()
                rgroups[grp][pip].add(bit)

        shared_bits = dict()
        for bit, pips in routebits_routezbits:
            for pip in pips:
                grp_name = ".".join(pip.split('.')[:-1])
                if bit not in shared_bits:
                    shared_bits[bit] = set()
                shared_bits[bit].add(grp_name)

        rgroups_with_title = list()

        for grp, gdata in sorted(rgroups.items()):
            title = ""
            for pip, bits in gdata.items():
                for bit in bits:
                    if bit in piptypes:
                        # title = piptypes[bit] + "-"
                        pass
                    else:
                        print("Detected DB error in PIP %s %s" % (pip, bits))
            title += "PIPs driving " + ", ".join(sorted(rgroup_names[grp]))
            rgroups_with_title.append((title, grp, gdata))

        for title, grp, gdata in sorted(rgroups_with_title):
            grp_bits = set()
            for pip, bits in gdata.items():
                grp_bits |= bits

            def bit_key(b):
                if segtype in ["hclk_l", "hclk_r"]:
                    if b in hclk_left_bits:
                        return "a" + b
                    if b in hclk_right_bits:
                        return "c" + b
                if segtype in ["clblm_l", "clblm_r", "clbll_l", "clbll_r"]:
                    if b in clb_left_bits:
                        return "a" + b
                    if b in clb_right_bits:
                        return "c" + b
                return "b" + b

            grp_bits = sorted(grp_bits, key=bit_key)

            for bit in grp_bits:
                print("<a id=\"b%s\"/>" % bit, file=f)

            print("<script><!--", file=f)
            print("grp2bits['%s'] = ['%s'];" % (grp_bits[0], "', '".join(grp_bits)), file=f)
            for bit in grp_bits:
                print("bit2grp['%s'] = '%s';" % (bit, grp_bits[0]), file=f)
            print("//--></script>", file=f)

            print("<p/>", file=f)
            print("<h4>%s</h4>" % title, file=f)
            print("<table cellspacing=0>", file=f)
            print("<tr><th width=\"400\" align=\"left\">PIP</th>", file=f)

            for bit in grp_bits:
                print("<th>&nbsp;%s&nbsp;</th>" % bit, file=f)
            print("</tr>", file=f)

            lines = list()
            for pip, bits in sorted(gdata.items()):
                line = " --><td>%s</td>" % (pip)
                for bit in grp_bits:
                    c = "-"
                    if bit in routebits[segtype]  and pip in routebits[segtype][bit]:  c = "1"
                    if bit in routezbits[segtype] and pip in routezbits[segtype][bit]: c = "0"
                    line = "%s%s<td align=\"center\">%s</td>" % (c, line, c)
                lines.append(line)

            trstyle = ""
            for line in sorted(lines):
                trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
                print("<tr%s><!-- %s</tr>" % (trstyle, line), file=f)

            print("</table>", file=f)

            first_note = True
            for bit in grp_bits:
                if len(shared_bits[bit]) > 1:
                    if first_note:
                        print("<p><b>Note(s):</b><br/>", file=f)
                    print("Warning: Groups sharing bit %s: %s." % (bit, ", ".join(sorted(shared_bits[bit]))))
                    print("Groups sharing bit <b>%s</b>: %s.<br/>" % (bit, ", ".join(sorted(shared_bits[bit]))), file=f)
                    first_note = False
            if not first_note:
                print("</p>", file=f)

        for tile_type in segtiles[segtype]:
            print("<h3>Tile %s Pseudo PIPs</h3>" % tile_type, file=f)
            print("<table cellspacing=0>", file=f)
            print("<tr><th width=\"500\" align=\"left\">PIP</th><th>Type</th></tr>", file=f)
            trstyle = ""
            with db_open("ppips_%s.db" % tile_type.lower()) as fi:
                for line in fi:
                    pip_name, pip_type = line.split()
                    trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
                    print("<tr%s><td>%s</td><td>%s</td></tr>" % (trstyle, pip_name, pip_type), file=f)
            print("</table>", file=f)

        print("</div>", file=f)
        print("</body></html>", file=f)
