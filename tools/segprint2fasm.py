#!/usr/bin/env python3

import os
import re
import sys
import json


def tag2fasm(grid, seg, tag):
    '''Given tilegrid, segment name and tag, return fasm directive'''
    segj = grid['segments'][seg]

    def clbf(seg, tile, tag_post):
        # seg: SEG_CLBLM_L_X10Y102
        # tile_type: CLBLM_L
        # tag_post: SLICEM_X0.ALUT.INIT[43]
        # To: CLBLM_L_X10Y102.SLICE_X12Y102.ALUT.INIT[43] 1
        m = re.match(r'(SLICE[LM])_X([01])[.](.*)', tag_post)
        slicelm = m.group(1)
        off01 = int(m.group(2))
        post = m.group(3)

        # xxx: actually this might not work on decimal overflow (9 => 10)
        for site in grid['tiles'][tile]['sites'].keys():
            m = re.match(r'SLICE_X(.*)Y.*', site)
            sitex = int(m.group(1))
            if sitex % 2 == off01:
                break
        else:
            raise Exception("Failed to match site")

        return '%s.%s.%s 1' % (tile, site, post)

    def intf(seg, tile, tag_post):
        # Make the selection an argument of the configruation
        m = re.match(r'(.*)[.]([A-Za-z0-9_]+)', tag_post)
        which = m.group(1)
        value = m.group(2)
        site = {
            'clbll_l': 'CENTER_INTER_L',
            'clbll_r': 'CENTER_INTER_R',
            'clblm_l': 'CENTER_INTER_L',
            'clblm_r': 'CENTER_INTER_R',
            'hclk_l': 'HCLK_L',
            'hclk_r': 'HCLK_R',
        }[segj['type']]
        return '%s.%s.%s %s' % (tile, site, which, value)

    m = re.match(r'([A-Za-z0-9_]+)[.](.*)', tag)
    tile_type = m.group(1)
    tag_post = m.group(2)

    # Find associated tile
    for tile in segj['tiles']:
        if grid['tiles'][tile]['type'] == tile_type:
            break
    else:
        raise Exception("Couldn't find tile type %s" % tile_type)

    tag2asm = {
        'CLBLL_L': clbf,
        'CLBLL_R': clbf,
        'CLBLM_L': clbf,
        'CLBLM_R': clbf,
        'INT_L': intf,
        'INT_R': intf,
        'HCLK_L': intf,
        'HCLK_R': intf,
    }
    f = tag2asm.get(tile_type, None)
    if f is None:
        raise Exception("Unhandled segment type %s" % tile_type)
    return f(seg, tile, tag_post)


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
