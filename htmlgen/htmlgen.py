#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# https://symbiflow.github.io/prjxray-db/
# https://symbiflow.github.io/prjxray-db/artix7/

import os, sys, json, re
from io import StringIO
from prjxray.util import get_fabric_for_part


def mk_get_setting(settings_filename):
    if settings_filename:
        settings = {}
        with open(settings_filename) as f:
            for line in f:
                line = line.strip()
                if not line.startswith("export "):
                    continue
                key, value = line[7:].split('=', 1)
                settings[key] = value[1:-1]

        assert len(settings), (settings_filename, settings)
        assert settings['XRAY_DATABASE'], pprint.pformat(settings)
        settings['XRAY_DATABASE_DIR'] = os.path.abspath(
            os.path.join(
                os.path.dirname(settings_filename),
                '..',
                'database',
            ), )
        return lambda name: settings[name]
    else:
        return os.getenv


get_setting = mk_get_setting(None)


def db_open(fn, db_dir):
    filename = os.path.join(db_dir, fn)
    if not os.path.exists(filename):
        return StringIO("")
    return open(os.path.join(db_dir, fn))


def out_open(fn, output):
    os.makedirs(output, exist_ok=True)
    fp = os.path.join(output, fn)
    print("Writing %s" % fp)
    return open(fp, "w")


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


def db_read(dbstate, tiletype, db_dir):
    dbstate.cfgbits[tiletype] = dict()
    dbstate.cfgbits_r[tiletype] = dict()
    dbstate.maskbits[tiletype] = set()
    dbstate.ppips[tiletype] = dict()
    dbstate.routebits[tiletype] = dict()
    dbstate.routezbits[tiletype] = dict()

    def add_pip_bits(tag, bits):
        if tag not in dbstate.routebits[tiletype]:
            dbstate.routebits[tiletype][tag] = set()
            dbstate.routezbits[tiletype][tag] = set()
        for bit in bits:
            if bit[0] == "!":
                if bit[1:] not in dbstate.routezbits[tiletype]:
                    dbstate.routezbits[tiletype][bit[1:]] = set()
                dbstate.routezbits[tiletype][bit[1:]].add(tag)
            else:
                if bit not in dbstate.routebits[tiletype]:
                    dbstate.routebits[tiletype][bit] = set()
                dbstate.routebits[tiletype][bit].add(tag)

    def add_cfg_bits(tag, bits):
        if tag not in dbstate.cfgbits[tiletype]:
            dbstate.cfgbits[tiletype][tag] = set()
        for bit in bits:
            dbstate.cfgbits[tiletype][tag].add(bit)
            if bit not in dbstate.cfgbits_r[tiletype]:
                dbstate.cfgbits_r[tiletype][bit] = set()
            dbstate.cfgbits_r[tiletype][bit].add(tag)

    with db_open("segbits_%s.db" % tiletype, db_dir) as f:
        for line in f:
            line = line.split()
            tag, bits = line[0], line[1:]

            if tiletype in ["int_l", "int_r", "hclk_l", "hclk_r"]:
                add_pip_bits(tag, bits)

            elif tiletype in ["clbll_l", "clbll_r", "clblm_l", "clblm_r"] and \
                    re.search(r"(\.[ABCD].*MUX\.)|(\.PRECYINIT\.)", tag):
                add_pip_bits(tag, bits)

            else:
                add_cfg_bits(tag, bits)

    with db_open("ppips_%s.db" % tiletype, db_dir) as f:
        for line in f:
            tag, typ = line.split()
            dbstate.ppips[tiletype][tag] = typ

    if tiletype not in ["int_l", "int_r"]:
        with db_open("mask_%s.db" % tiletype, db_dir) as f:
            for line in f:
                tag, bit = line.split()
                assert tag == "bit"
                dbstate.maskbits[tiletype].add(bit)
    else:
        for t in ["clbll_l", "clbll_r", "clblm_l", "clblm_r", "dsp_l", "dsp_r",
                  "bram_l", "bram_r"]:
            with db_open("mask_%s.db" % t, db_dir) as f:
                for line in f:
                    tag, bit = line.split()
                    assert tag == "bit"
                    frameidx, bitidx = bit.split("_")
                    dbstate.maskbits[tiletype].add(
                        "%02d_%02d" % (int(frameidx), int(bitidx) % 64))


def init_bitdb():
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
        clb_bitgroups_db.append(
            "02_%02d 03_%02d 05_%02d 06_%02d 07_%02d|05_%02d 03_%02d 04_%02d 04_%02d"
            % (i + 1, i, i, i, i + 1, i + 3, i + 1, i + 1, i + 2))
        clb_bitgroups_db.append(
            "02_%02d 04_%02d 05_%02d 05_%02d 06_%02d|02_%02d 03_%02d 04_%02d 07_%02d"
            % (i + 2, i, i + 1, i + 2, i + 2, i + 3, i + 2, i + 3, i + 3))

    return clb_bitgroups_db, hclk_bitgroups_db


def init_hclk_bits(hclk_bitgroups_db):
    hclk_left_bits = set()
    hclk_right_bits = set()

    for entry in hclk_bitgroups_db:
        a, b = entry.split("|")
        for bit in a.split():
            hclk_left_bits.add(bit)
        for bit in b.split():
            hclk_right_bits.add(bit)

    return hclk_left_bits, hclk_right_bits


def init_clb_bits(clb_bitgroups_db):
    clb_left_bits = set()
    clb_right_bits = set()

    for entry in clb_bitgroups_db:
        a, b = entry.split("|")
        for bit in a.split():
            clb_left_bits.add(bit)
        for bit in b.split():
            clb_right_bits.add(bit)

    return clb_left_bits, clb_right_bits


class DBState():
    def __init__(self):
        self.cfgbits = dict()
        self.cfgbits_r = dict()
        self.maskbits = dict()
        self.ppips = dict()
        self.routebits = dict()
        self.routezbits = dict()


class Tweaks():
    def __init__(self):
        pass


def load_tilegrid(db_dir, fabric, verbose=False, allow_fake=False):
    print("Loading tilegrid.")
    with db_open(os.path.join(fabric, "tilegrid.json"), db_dir) as f:
        data = f.read()
        if not data:
            assert allow_fake, 'No tilegrid.json found'
            print('WARNING: loading fake tilegrid')
            grid = {
                "NULL": {
                    "grid_x": 0,
                    "grid_y": 0,
                    "type": "NULL",
                }
            }
        else:
            grid = json.loads(data)
    return grid


def db_reads(dbstate, db_dir):

    db_read(dbstate, "int_l", db_dir)
    db_read(dbstate, "int_r", db_dir)

    db_read(dbstate, "hclk_l", db_dir)
    db_read(dbstate, "hclk_r", db_dir)

    db_read(dbstate, "clbll_l", db_dir)
    db_read(dbstate, "clbll_r", db_dir)

    db_read(dbstate, "clblm_l", db_dir)
    db_read(dbstate, "clblm_r", db_dir)

    db_read(dbstate, "dsp_l", db_dir)
    db_read(dbstate, "dsp_r", db_dir)

    db_read(dbstate, "bram_l", db_dir)
    db_read(dbstate, "bram_r", db_dir)


def place_tiles(grid):
    grid_map = dict()
    grid_range = None

    for tilename, tiledata in grid.items():
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
    return grid_map, grid_range


def tile_bgcolor(tiledata):
    bgcolor = "#eeeeee"

    # INT - Blue
    if tiledata["type"] in ["INT_L", "INT_R"]: bgcolor = "#aaaaff"
    elif "INT_FEEDTHRU" in tiledata["type"]: bgcolor = "#ddddff"

    # CLBL - Yellow
    if tiledata["type"] in ["CLBLL_L", "CLBLL_R"]: bgcolor = "#ffffaa"
    # CLBM - Red
    if tiledata["type"] in ["CLBLM_L", "CLBLM_R"]: bgcolor = "#ffaaaa"

    # CLK - Green
    if tiledata["type"] in ["HCLK_L", "HCLK_R"]: bgcolor = "#aaffaa"
    elif "CLK" in tiledata["type"]: bgcolor = "#66ff66"
    elif "CMT" in tiledata["type"]: bgcolor = "#22ff22"

    # BRAM - Cyan
    if tiledata["type"] in ["BRAM_INT_INTERFACE_L", "BRAM_L"]:
        bgcolor = "#aaffff"
    if tiledata["type"] in ["BRAM_INT_INTERFACE_R", "BRAM_R"]:
        bgcolor = "#aaffff"

    # DSP - Purple
    if tiledata["type"] in ["INT_INTERFACE_L", "DSP_L"]:
        bgcolor = "#ffaaff"
    if tiledata["type"] in ["INT_INTERFACE_R", "DSP_R"]:
        bgcolor = "#ffaaff"

    if "IO" in tiledata["type"]:
        bgcolor = "#dddddd"

    # Unused - grey
    if tiledata["type"] in ["NULL", "VBRK"] or "BRK" in tiledata["type"]:
        bgcolor = "#aaaaaa"

    return bgcolor


def tile_print_td(f, title, tilename, bgcolor, tiledata, dbstate):
    tilename = tilename.replace("INT_INTERFACE_", "INTF_")
    tilename = tilename.replace("_X", "<br/>X")
    tilename = tilename.replace("B_TERM", "B<br/>TERM")

    print(
        "<td bgcolor=\"%s\" align=\"center\" title=\"%s\"><span style=\"font-size:10px\">"
        % (bgcolor, "\n".join(title)),
        file=f)
    if tiledata["type"].lower() in dbstate.cfgbits:
        print(
            "<a style=\"text-decoration: none; color: black\" href=\"tile_%s.html\">%s</a></span></td>"
            % (tiledata["type"].lower(), tilename.replace("_X", "<br/>X")),
            file=f)
    else:
        print(
            "%s</span></td>" % tilename.replace("_X", "<br/>X").replace(
                "B_TERM", "B<br/>TERM"),
            file=f)


def tile_title(tilename, tiledata, grid_x, grid_y, grid):
    title = [tilename]
    segdata = None

    if "segment" in tiledata:
        # FIXME: BRAM support
        segdata = grid[tilename]['bits'].get('CLB_IO_CLK', None)
        title.append(tiledata["segment"])

    title.append("GRID_POSITION: %d %d" % (grid_x, grid_y))

    if "sites" in tiledata:
        for sitename, sitetype in tiledata["sites"].items():
            title.append("%s site: %s" % (sitetype, sitename))

    if segdata:
        if "baseaddr" in segdata:
            #title.append("Baseaddr: %s %d" % tuple(segdata["baseaddr"]))
            title.append("Baseaddr: %s" % segdata["baseaddr"])
        else:
            print(
                "Warning: no baseaddr in segment %s (via tile %s)." %
                (tiledata["segment"], tilename))

    return title


def mk_tilegrid_page(dbstate, output, grid):
    with out_open("index.html", output) as f:
        print(
            "<html><title>X-Ray %s Database</title><body>" %
            get_setting("XRAY_DATABASE").upper(),
            file=f)
        print(
            "<h3>X-Ray %s Database</h3>" %
            get_setting("XRAY_DATABASE").upper(),
            file=f)

        print(
            "<p><b>Part: %s<br/>ROI TILEGRID: %s<br/>ROI Frames: %s</b></p>" %
            (
                get_setting("XRAY_PART"), get_setting("XRAY_ROI_TILEGRID"),
                get_setting("XRAY_ROI_FRAMES")),
            file=f)

        grid_map, grid_range = place_tiles(grid)

        print("<table border>", file=f)

        for grid_y in range(grid_range[1], grid_range[3] + 1):
            print("<tr>", file=f)

            for grid_x in range(grid_range[0], grid_range[2] + 1):
                tilename = grid_map[(grid_x, grid_y)]
                tiledata = grid[tilename]

                bgcolor = tile_bgcolor(tiledata)
                title = tile_title(tilename, tiledata, grid_x, grid_y, grid)
                tile_print_td(f, title, tilename, bgcolor, tiledata, dbstate)

            print("</tr>", file=f)

        print("</table>", file=f)
        print("</body></html>", file=f)


def get_bit_name(dbstate, frameidx, bitidx, bit_pos, tiletype):
    bit_name = dbstate.cfgbits_r[tiletype][
        bit_pos] if bit_pos in dbstate.cfgbits_r[tiletype] else None

    if bit_name is None and bit_pos in dbstate.routebits[tiletype]:
        bit_name = dbstate.routebits[tiletype][bit_pos]

    if bit_name is None and bit_pos in dbstate.routezbits[tiletype]:
        bit_name = dbstate.routezbits[tiletype][bit_pos]

    if bit_name is None and tiletype in ["clbll_l", "clbll_r", "clblm_l",
                                         "clblm_r", "dsp_l", "dsp_r", "bram_l",
                                         "bram_r"]:
        int_tile_type = "int_" + tiletype[-1]
        bit_int_pos = "%02d_%02d" % (frameidx, bitidx % 64)
        bit_name = dbstate.cfgbits_r[int_tile_type][
            bit_int_pos] if bit_int_pos in dbstate.cfgbits_r[
                int_tile_type] else None

        if bit_name is None and bit_int_pos in dbstate.routebits[int_tile_type]:
            bit_name = dbstate.routebits[int_tile_type][bit_int_pos]

        if bit_name is None and bit_int_pos in dbstate.routezbits[
                int_tile_type]:
            bit_name = dbstate.routezbits[int_tile_type][bit_int_pos]

    if bit_name is not None:
        if len(bit_name) <= 1:
            bit_name = "".join(bit_name)
        else:
            for n in bit_name:
                bit_name = ".".join(n.split(".")[:-1])

    return bit_name


def get_bit_info(dbstate, frameidx, bitidx, tiletype):
    bit_pos = "%02d_%02d" % (frameidx, bitidx)

    bit_name = get_bit_name(dbstate, frameidx, bitidx, bit_pos, tiletype)

    label = None
    title = [bit_pos]
    bgcolor = "#aaaaaa"

    if bit_pos not in dbstate.maskbits[tiletype]:
        label = "&nbsp;"
        bgcolor = "#444444"
        title.append("UNUSED ?")

    if (tiletype in ["hclk_l", "hclk_r"]) and bitidx < 13:
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

        m = re.search(r"\.([ABCD])LUT.DI1MUX\.", bit_name)
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

        if re.match("^INT_[LR].[SNWE][SNWERL]", bit_name):
            if bit_name[8] == "1":
                bgcolor = "#4466bb"
            elif bit_name[8] == "2":
                bgcolor = "#aa88ff"
            elif bit_name[6:9] in "SS6 SE6 NN6 NW6".split():
                bgcolor = "#7755ff"
            else:
                bgcolor = "#88aaff"
            label = bit_name[6:9]

        if re.match("^INT_[LR].IMUX", bit_name):
            m = re.match("^INT_[LR].IMUX(_L)?(\\d+)", bit_name)
            bgcolor = "#88aaff"
            label = "IM" + m.group(2)

        if re.match("^INT_[LR].BYP_ALT", bit_name):
            bgcolor = "#7755ff"
            label = "BA" + bit_name[13]

        if re.match("^INT_[LR].FAN_ALT", bit_name):
            bgcolor = "#4466bb"
            label = "FA" + bit_name[13]

        if re.match("^INT_[LR].CLK", bit_name):
            bgcolor = "#4466bb"
            label = "CLK"

        if re.match("^INT_[LR].CTRL", bit_name):
            bgcolor = "#7755ff"
            label = "CTRL"

        if re.match("^INT_[LR].GFAN", bit_name):
            bgcolor = "#7755ff"
            label = "GFAN"

        if re.match("^INT_[LR].LVB", bit_name):
            bgcolor = "#88aaff"
            label = "LVB"

        if re.match("^INT_[LR].LV", bit_name):
            bgcolor = "#88aaff"
            label = "LV"

        if re.match("^INT_[LR].LH", bit_name):
            bgcolor = "#4466bb"
            label = "LH"

        if re.match("^CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]5?FFMUX", bit_name):
            bgcolor = "#88aaff"
            label = "DMX"

        if re.match("^CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]OUTMUX", bit_name):
            bgcolor = "#aa88ff"
            label = "OMX"

        if re.match("^CLBL[LM]_[LR].SLICE[LM]_X[01].PRECYINIT", bit_name):
            bgcolor = "#88aaff"
            label = "CYI"

        if re.match("^HCLK_[LR]", bit_name) and "_B_BOT" in bit_name:
            bgcolor = "#4466bb"
            label = "BOT"

        if re.match("^HCLK_[LR]", bit_name) and "_B_TOP" in bit_name:
            bgcolor = "#7755ff"
            label = "TOP"

        if re.match("^DSP_[LR].DSP_[01].(PATTERN|MASK)", bit_name):
            bgcolor = "#ffffaa"
            label = bit_name[12] + bit_name[10]

    return bit_pos, label, title, bgcolor


def gen_table(dbstate, tiletype, f):
    print(
        """
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
    """,
        file=f)

    num_frames = 36
    unused_bits = 0
    unknown_bits = 0
    known_bits = 0
    hideframes = set()

    if tiletype in ["int_l", "int_r", "hclk_l", "hclk_r"]:
        num_frames = 26

    if tiletype in ["bram_l", "bram_r", "dsp_l", "dsp_r"]:
        for i in range(5, 25):
            hideframes.add(i)
        num_frames = 28

    height = 2
    if tiletype in ["hclk_l", "hclk_r"]:
        height = 1
    if tiletype in ["dsp_l", "dsp_r", "bram_l", "bram_r"]:
        height = 10

    if height > 2:
        print("<table><tr><td>", file=f)

    def print_table_header():
        print("<table border>", file=f)
        print("<tr>", file=f)
        print("<th width=\"30\"></th>", file=f)
        for frameidx in range(num_frames):
            if frameidx in hideframes:
                continue
            print(
                "<th width=\"30\"><span style=\"font-size:10px\">%d</span></th>"
                % frameidx,
                file=f)
        print("</tr>", file=f)

    print_table_header()

    for bitidx in range(32 * height - 1, -1, -1):
        print("<tr>", file=f)
        print(
            "<th align=\"right\"><span style=\"font-size:10px\">%d</span></th>"
            % bitidx,
            file=f)
        for frameidx in range(num_frames):
            if frameidx in hideframes:
                continue

            bit_pos, label, title, bgcolor = get_bit_info(
                dbstate, frameidx, bitidx, tiletype)

            if label is None:
                label = "&nbsp;"

            if label == "INT":
                onclick = " onmousedown=\"location.href = 'tile_int_%s.html#b%s'\"" % (
                    tiletype[-1], bit_pos)
            else:
                onclick = " onmousedown=\"location.href = '#b%s'\"" % bit_pos

            if bgcolor == "#aaaaaa":
                unknown_bits += 1
            elif bgcolor == "#444444":
                unused_bits += 1
            else:
                known_bits += 1

            print(
                "<td id=\"bit%s\" onmouseenter=\"ome('%s');\" onmouseleave=\"oml();\" bgcolor=\"%s\" align=\"center\" title=\"%s\"%s><span style=\"font-size:10px\">%s</span></td>"
                %
                (bit_pos, bit_pos, bgcolor, "\n".join(title), onclick, label),
                file=f)
        print("</tr>", file=f)

        if bitidx > 0 and bitidx % 80 == 0:
            print("</table></td><td>", file=f)
            print_table_header()

    print("</table>", file=f)

    if height > 2:
        print("</td></tr></table>", file=f)

    print(
        "  unused: %d, unknown: %d, known: %d, total: %d, percentage: %.2f%% (%.2f%%)"
        % (
            unused_bits, unknown_bits, known_bits,
            unused_bits + unknown_bits + known_bits, 100 * known_bits /
            (unknown_bits + unused_bits + known_bits), 100 *
            (known_bits + unused_bits) /
            (unknown_bits + unused_bits + known_bits)))


def mk_segment_pages(dbstate, output, tweaks):
    for tiletype in sorted(dbstate.cfgbits.keys()):
        with out_open("tile_%s.html" % tiletype, output) as f:
            print(
                "<html><title>X-Ray %s Database: %s</title><body>" %
                (get_setting("XRAY_DATABASE").upper(), tiletype.upper()),
                file=f)
            print(
                "<h3><a href=\"index.html\">X-Ray %s Database</a>: %s Segment</h3>"
                % (get_setting("XRAY_DATABASE").upper(), tiletype.upper()),
                file=f)

            gen_table(dbstate, tiletype, f)

            print("<div>", file=f)

            bits_by_prefix = dict()

            for bit_name, bits_pos in dbstate.cfgbits[tiletype].items():
                prefix = ".".join(bit_name.split(".")[0:-1])

                if prefix not in bits_by_prefix:
                    bits_by_prefix[prefix] = set()

                for bit_pos in bits_pos:
                    bits_by_prefix[prefix].add((bit_name, bit_pos))

            for prefix, bits in sorted(bits_by_prefix.items()):
                for bit_name, bit_pos in sorted(bits):
                    print("<a id=\"b%s\"/>" % bit_pos, file=f)

                print("<p/>", file=f)
                print("<h4>%s</h4>" % prefix, file=f)
                print("<table cellspacing=0>", file=f)
                print(
                    "<tr><th width=\"400\" align=\"left\">Bit Name</th><th>Position</th></tr>",
                    file=f)

                trstyle = ""
                for bit_name, bit_pos in sorted(bits):
                    trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
                    print(
                        "<tr%s><td>%s</td><td>%s</td></tr>" %
                        (trstyle, bit_name, bit_pos),
                        file=f)

                print("</table>", file=f)

            ruf = UnionFind()
            routebits_routezbits = list(dbstate.routebits[tiletype].items())
            routebits_routezbits += list(dbstate.routezbits[tiletype].items())

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
                title = "PIPs driving " + ", ".join(sorted(rgroup_names[grp]))
                rgroups_with_title.append((title, grp, gdata))

            for title, grp, gdata in sorted(rgroups_with_title):
                grp_bits = set()
                for pip, bits in gdata.items():
                    grp_bits |= bits

                def bit_key(b):
                    if tiletype in ["hclk_l", "hclk_r"]:
                        if b in tweaks.hclk_left_bits:
                            return "a" + b
                        if b in tweaks.hclk_right_bits:
                            return "c" + b
                    if tiletype in ["clblm_l", "clblm_r", "clbll_l", "clbll_r",
                                    "int_l", "int_r"]:
                        if b in tweaks.clb_left_bits:
                            return "a" + b
                        if b in tweaks.clb_right_bits:
                            return "c" + b
                    return "b" + b

                grp_bits = sorted(grp_bits, key=bit_key)

                for bit in grp_bits:
                    print("<a id=\"b%s\"/>" % bit, file=f)

                print("<script><!--", file=f)
                print(
                    "grp2bits['%s'] = ['%s'];" %
                    (grp_bits[0], "', '".join(grp_bits)),
                    file=f)
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
                        if bit in dbstate.routebits[
                                tiletype] and pip in dbstate.routebits[
                                    tiletype][bit]:
                            c = "1"
                        if bit in dbstate.routezbits[
                                tiletype] and pip in dbstate.routezbits[
                                    tiletype][bit]:
                            c = "0"
                        line = "%s%s<td align=\"center\">%s</td>" % (
                            c, line, c)
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
                        print(
                            "Warning: Groups sharing bit %s: %s." %
                            (bit, ", ".join(sorted(shared_bits[bit]))))
                        print(
                            "Groups sharing bit <b>%s</b>: %s.<br/>" %
                            (bit, ", ".join(sorted(shared_bits[bit]))),
                            file=f)
                        first_note = False
                if not first_note:
                    print("</p>", file=f)

            if len(dbstate.ppips[tiletype]) > 0:
                print("<h4>Pseudo PIPs</h4>", file=f)
                print("<table cellspacing=0>", file=f)
                print(
                    "<tr><th width=\"500\" align=\"left\">PIP</th><th>Type</th></tr>",
                    file=f)
                trstyle = ""
                for typ, tag in sorted(
                    [(b, a) for a, b in dbstate.ppips[tiletype].items()]):
                    trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
                    print(
                        "<tr%s><td>%s</td><td>%s</td></tr>" %
                        (trstyle, tag, typ),
                        file=f)
                print("</table>", file=f)

            print("</div>", file=f)
            print("</body></html>", file=f)


def run(settings, output, verbose=False, allow_fake=False):
    global get_setting

    get_setting = mk_get_setting(settings)

    if output is None:
        output = os.path.join(
            os.path.curdir, 'html', get_setting('XRAY_DATABASE'))

    db_dir = os.path.join(
        get_setting("XRAY_DATABASE_DIR"), get_setting("XRAY_DATABASE"))

    # Load tweaks
    tweaks = Tweaks()
    clb_bitgroups_db, hclk_bitgroups_db = init_bitdb()
    tweaks.hclk_left_bits, tweaks.hclk_right_bits = init_hclk_bits(
        hclk_bitgroups_db)
    tweaks.clb_left_bits, tweaks.clb_right_bits = init_clb_bits(
        clb_bitgroups_db)

    # Load source data
    dbstate = DBState()
    fabric = get_fabric_for_part(db_dir, get_setting("XRAY_PART"))
    grid = load_tilegrid(
        db_dir, fabric, verbose=verbose, allow_fake=allow_fake)
    db_reads(dbstate, db_dir)

    # Create pages
    mk_tilegrid_page(dbstate, output, grid)
    mk_segment_pages(dbstate, output, tweaks)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a pretty HTML version of the documentation.")
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument(
        '--output',
        default=None,
        help='Put the generated files in this directory (default current dir).'
    )
    parser.add_argument(
        '--settings',
        default=None,
        help='Read the settings from file (default to environment).',
    )
    parser.add_argument(
        '--allow-fake',
        default=False,
        action='store_true',
        help="Continue even if tilegrid.json isn't found.",
    )

    args = parser.parse_args()
    run(
        settings=args.settings,
        output=args.output,
        verbose=args.verbose,
        allow_fake=args.allow_fake,
    )


if __name__ == '__main__':
    main()
