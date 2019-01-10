#!/usr/bin/env python3

import re
from prjxray import bitsmaker


def mktag(tile, dframe, dword, dbit, multi=False):
    # mimicing tag names, wasn't sure if it would break things otherwise
    metastr = "DWORD:%u" % dword
    if dbit is not None:
        metastr += ".DBIT:%u" % dbit
    if dframe is not None:
        metastr += ".DFRAME:%02x" % dframe
    if multi:
        metastr += ".MULTI"
    return "%s.%s" % (tile, metastr)


def run(
        fnout="segdata_tilegrid.txt",
        bits_fn="design.bits",
        design_fn="design.csv",
        oneval="KEEPER",
        verbose=False):
    """
    LIOB33_SING_X0Y100  LIOB33_SING     00020026_000_28
    LIOB33_X0Y101                       00020027_003_03
    LIOB33_X0Y101                       00020026_004_28
    LIOB33_X0Y103       LIOB33          00020027_007_03
    .
    LIOB33_X0Y105       LIOB33          00020027_011_03
    .
    ...
    LIOB33_X0Y143       LIOB33          00020027_088_03
    LIOB33_X0Y145       LIOB33          00020027_092_03
    LIOB33_X0Y147       LIOB33          00020027_096_03
    LIOB33_SING_X0Y149  LIOB33_SING     00020027_100_03
    """

    # convert either Y0 or Y1 position to relative offsets
    dy2delta = {
        # (dframe, dword, dbit)
        0: (0x26, 2, 28),
        1: (0x27, 1, 3),
    }

    tags = dict()
    f = open(design_fn, 'r')
    f.readline()
    for l in f:
        l = l.strip()
        tile, val, site, site_type = l.split(',')[0:4]
        # IOB_X0Y118 => 118 => 0
        y = int(re.search(r"_X[0-9]+Y([0-9]+)", site).group(1))
        dy = y % 2
        drame, dword, dbit = dy2delta[dy]
        tags[mktag(tile, drame, dword, dbit)] = val == oneval

    bitsmaker.write(bits_fn, fnout, tags)


if __name__ == "__main__":
    run()
