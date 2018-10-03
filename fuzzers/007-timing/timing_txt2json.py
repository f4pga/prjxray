#!/usr/bin/env python3

from timfuz import Benchmark, A_di2ds
import glob
import math
import json
import sys
from collections import OrderedDict

# Speed index: some sort of special value
SI_NONE = 0xFFFF


def parse_pip(s, speed_i2s):
    # Entries like
    # CLK_BUFG_REBUF_X60Y117/CLK_BUFG_REBUF.CLK_BUFG_REBUF_R_CK_GCLK0_BOT<<->>CLK_BUFG_REBUF_R_CK_GCLK0_TOP
    # Convert to (site, type, pip_junction, pip)
    pipstr, speed_index = s.split(':')
    speed_index = int(speed_index)
    site, instance = pipstr.split('/')
    #type, pip_junction, pip = others.split('.')
    #return (site, type, pip_junction, pip)
    return site, instance, speed_i2s[int(speed_index)]


def parse_pips(pips, speed_i2s):
    if not pips:
        return []
    return [parse_pip(pip, speed_i2s) for pip in pips.split('|')]


def parse_node(s):
    node, nwires = s.split(':')
    return node, int(nwires)


def parse_nodes(nodes):
    if not nodes:
        return []
    return [parse_node(node) for node in nodes.split('|')]


def parse_wire(s, speed_i2s):
    # CLBLM_R_X3Y80/CLBLM_M_D6:952
    wirestr, speed_index = s.split(':')
    site, instance = wirestr.split('/')
    return site, instance, speed_i2s[int(speed_index)]


def parse_wires(wires, speed_i2s):
    if not wires:
        return []
    return [parse_wire(wire, speed_i2s) for wire in wires.split('|')]


def gen_timing4(fn, speed_i2s):
    f = open(fn, 'r')
    header_want = "linetype,net,src_site,src_site_type,src_site_pin,src_bel,src_bel_pin,dst_site,dst_site_type,dst_site_pin,dst_bel,dst_bel_pin,ico,fast_max,fast_min,slow_max,slow_min,pips,inodes,wires"
    ncols = len(header_want.split(','))

    # src_bel dst_bel ico fast_max fast_min slow_max slow_min pips
    header_got = f.readline().strip()
    if header_got != header_want:
        raise Exception("Unexpected columns")

    rets = 0
    # XXX: there were malformed lines, but think they are fixed now?
    bads = 0
    net_lines = 0
    for l in f:

        def group_line():
            ncols = len('lintype,ico,delays'.split(','))
            assert len(parts) == ncols
            _lintype, ico, delays = parts
            return int(ico), int(delays)

        def net_line():
            assert len(parts) == ncols, "Expected %u parts, got %u" % (
                ncols, len(parts))
            _lintype, net, src_site, src_site_type, src_site_pin, src_bel, src_bel_pin, dst_site, dst_site_type, dst_site_pin, dst_bel, dst_bel_pin, ico, fast_max, fast_min, slow_max, slow_min, pips, nodes, wires = parts
            return {
                'net': net,
                'src': {
                    'site': src_site,
                    'site_type': src_site_type,
                    'site_pin': src_site_pin,
                    'bel': src_bel,
                    'bel_pin': src_bel_pin,
                },
                'dst': {
                    'site': dst_site,
                    'site_type': dst_site_type,
                    'site_pin': dst_site_pin,
                    'bel': dst_bel,
                    'bel_pin': dst_bel_pin,
                },
                't': {
                    # ps
                    'fast_max': int(fast_max),
                    'fast_min': int(fast_min),
                    'slow_max': int(slow_max),
                    'slow_min': int(slow_min),
                },
                'ico': int(ico),
                'pips': parse_pips(pips, speed_i2s),
                'nodes': parse_nodes(nodes),
                'wires': parse_wires(wires, speed_i2s),
                'line': l,
            }

        l = l.strip()
        if not l:
            continue
        parts = l.split(',')
        lintype = parts[0]

        val = {
            'NET': net_line,
            'GROUP': group_line,
        }[lintype]()
        yield lintype, val

        rets += 1
    print('  load %s: %d bad, %d good lines' % (fn, bads, rets))


def gen_timing4n(fn, speed_i2s):
    '''Only generate nets'''
    for lintype, val in gen_timing4(fn, speed_i2s):
        if lintype == 'NET':
            yield val


def gen_timing4a(fn, speed_i2s):
    '''
    Like above, but aggregate ico + non-ico into single entries
    Key these based on uniqueness of (src_bel, dst_bel)

    ico 0 is followed by 1
    They should probably even be in the same order
    Maybe just assert that?
    '''
    entries = {}
    timgen = gen_timing4(fn, speed_i2s)
    rets = 0
    while True:

        def get_ico(exp_ico):
            ret = []
            try:
                lintype, val = next(timgen)
            except StopIteration:
                return None
            assert lintype == 'GROUP'
            ico, delays = val
            assert ico == exp_ico
            for _ in range(delays):
                lintype, val = next(timgen)
                assert lintype == 'NET'
                ret.append(val)
            return ret

        ico0s = get_ico(0)
        if ico0s is None:
            break
        ico1s = get_ico(1)
        # TODO: verify this is actually true
        assert len(ico0s) == len(ico1s)

        def same_path(l, r):
            # if source and dest are the same, should be the same thing
            return l['src']['bel_pin'] == r['src']['bel_pin'] and l['dst'][
                'bel_pin'] == r['dst']['bel_pin']

        for ico0, ico1 in zip(ico0s, ico1s):
            # TODO: verify this is actually true
            # otherwise move to more complex algorithm
            assert same_path(ico0, ico1)
            # aggregate timing info as (ic0, ic1) into ico0
            ico0['t'] = (
                ico0['t'],
                ico1['t'],
            )
            yield ico0
            rets += 1
    print('  load %s: %u aggregated lines' % (fn, rets))


def load_speed_json(f):
    j = json.load(f)
    # Index speed indexes to names
    speed_i2s = {}
    for k, v in j['speed_model'].items():
        i = v['speed_index']
        if i != SI_NONE:
            speed_i2s[i] = k
    return j, speed_i2s
