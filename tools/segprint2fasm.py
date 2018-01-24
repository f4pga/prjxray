#!/usr/bin/env python3

import os
import re
import sys
import json

enumdb = dict()


def get_enums(segtype):
    if segtype in enumdb:
        return enumdb[segtype]

    enumdb[segtype] = {}

    def process(l):
        l = l.strip()

        # CLBLM_L.SLICEL_X1.ALUT.INIT[10] 29_14
        parts = line.split()
        name = parts[0]
        bit_vals = parts[1:]

        # Assumption
        # only 1 bit => non-enumerated value
        enumdb[segtype][name] = len(bit_vals) != 1

    with open("%s/%s/segbits_%s.db" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE"), segtype),
              "r") as f:
        for line in f:
            process(line)

    with open("%s/%s/segbits_int_%s.db" %
              (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
               segtype[-1]), "r") as f:
        for line in f:
            process(line)

    return enumdb[segtype]


def isenum(segtype, tag):
    return get_enums(segtype)[tag]


def tag2fasm(grid, seg, tag):
    '''Given tilegrid, segment name and tag, return fasm directive'''
    segj = grid['segments'][seg]

    m = re.match(r'([A-Za-z0-9_]+)[.](.*)', tag)
    tile_type = m.group(1)
    tag_post = m.group(2)

    # Find associated tile
    for tile in segj['tiles']:
        if grid['tiles'][tile]['type'] == tile_type:
            break
    else:
        raise Exception("Couldn't find tile type %s" % tile_type)

    if not isenum(segj['type'], tag):
        return '%s.%s 1' % (tile, tag_post)
    else:
        # Make the selection an argument of the configruation
        m = re.match(r'(.*)[.]([A-Za-z0-9_]+)', tag_post)
        which = m.group(1)
        value = m.group(2)
        return '%s.%s %s' % (tile, which, value)


def run(f_in, f_out, sparse=False):
    with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        grid = json.load(f)

    seg = None
    for l in f_in:
        l = l.strip()
        if not l:
            continue
        # seg SEG_CLBLM_L_X10Y102
        # tag CLBLM_L.SLICEM_X0.ALUT.INIT[00]
        m = re.match('(seg|tag) (.*)', l)
        if not m:
            raise Exception("Invalid line %s" % l)
        type = m.group(1)
        if type == 'seg':
            seg = m.group(2)
        elif type == 'tag':
            f_out.write(tag2fasm(grid, seg, m.group(2)) + '\n')
        else:
            raise Exception("Invalid type %s" % type)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert segprint -d output to .fasm file (FPGA assembly)')

    parser.add_argument(
        'fn_in', default='/dev/stdin', nargs='?', help='Input segment file')
    parser.add_argument(
        'fn_out', default='/dev/stdout', nargs='?', help='Output .fasm file')

    args = parser.parse_args()
    run(open(args.fn_in, 'r'), open(args.fn_out, 'w'))
