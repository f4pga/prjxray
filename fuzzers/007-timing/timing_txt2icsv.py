#!/usr/bin/env python3

from timfuz import Benchmark, A_di2ds
import glob
import math
import json
import sys
from collections import OrderedDict

# Speed index: some sort of special value
SI_NONE = 0xFFFF

# prefix to make easier to track
# models do not overlap between PIPs and WIREs
PREFIX_W = 'WIRE_'
PREFIX_P = 'PIP_'


def parse_pip(s):
    # Entries like
    # CLK_BUFG_REBUF_X60Y117/CLK_BUFG_REBUF.CLK_BUFG_REBUF_R_CK_GCLK0_BOT<<->>CLK_BUFG_REBUF_R_CK_GCLK0_TOP
    # Convert to (site, type, pip_junction, pip)
    pipstr, speed_index = s.split(':')
    speed_index = int(speed_index)
    site, instance = pipstr.split('/')
    #type, pip_junction, pip = others.split('.')
    #return (site, type, pip_junction, pip)
    return site, instance, int(speed_index)


def parse_node(s):
    node, nwires = s.split(':')
    return node, int(nwires)


def parse_wire(s):
    # CLBLM_R_X3Y80/CLBLM_M_D6:952
    wirestr, speed_index = s.split(':')
    site, instance = wirestr.split('/')
    return site, instance, int(speed_index)


# FIXME: these actually have a delay element
# Probably need to put these back in
def remove_virtual_pips(pips):
    return pips
    return filter(lambda pip: not re.match(r'CLBL[LM]_[LR]_', pip[0]), pips)


def load_timing3(f, name='file'):
    # src_bel dst_bel ico fast_max fast_min slow_max slow_min pips
    f.readline()
    ret = []
    bads = 0
    for l in f:
        # FIXME: hack
        if 0 and 'CLK' in l:
            continue

        l = l.strip()
        if not l:
            continue
        parts = l.split(' ')
        # FIXME: deal with these nodes
        if len(parts) != 11:
            bads += 1
            continue
        net, src_bel, dst_bel, ico, fast_max, fast_min, slow_max, slow_min, pips, nodes, wires = parts
        pips = pips.split('|')
        nodes = nodes.split('|')
        wires = wires.split('|')
        ret.append(
            {
                'net': net,
                'src_bel': src_bel,
                'dst_bel': dst_bel,
                'ico': int(ico),
                # ps
                'fast_max': int(fast_max),
                'fast_min': int(fast_min),
                'slow_max': int(slow_max),
                'slow_min': int(slow_min),
                'pips': remove_virtual_pips([parse_pip(pip) for pip in pips]),
                'nodes': [parse_node(node) for node in nodes],
                'wires': [parse_wire(wire) for wire in wires],
                'line': l,
            })
    print('  load %s: %d bad, %d good' % (name, bads, len(ret)))
    #assert 0
    return ret


def load_speed_json(f):
    j = json.load(f)
    # Index speed indexes to names
    speed_i2s = {}
    for k, v in j['speed_model'].items():
        i = v['speed_index']
        if i != SI_NONE:
            speed_i2s[i] = k
    return j, speed_i2s


# Verify the nodes and wires really do line up
def vals2Adi_check(vals, names):
    print('Checking')
    for val in vals:
        node_wires = 0
        for _node, wiresn in val['nodes']:
            node_wires += wiresn
        assert node_wires == len(val['wires'])
    print('Done')
    assert 0


def vals2Adi(vals, speed_i2s, name_tr={}, name_drop=[], verbose=False):
    def pip2speed(pip):
        _site, _name, speed_index = pip
        return PREFIX_P + speed_i2s[speed_index]

    def wire2speed(wire):
        _site, _name, speed_index = wire
        return PREFIX_W + speed_i2s[speed_index]

    # Want this ordered
    names = OrderedDict()

    print(
        'Creating matrix w/ tr: %d, drop: %d' % (len(name_tr), len(name_drop)))

    # Take sites out entirely using handy "interconnect only" option
    #vals = filter(lambda x: str(x).find('SLICE') >= 0, vals)
    # Highest count while still getting valid result

    # First index all of the given pip types
    # Start out as set then convert to list to keep matrix order consistent
    sys.stdout.write('Indexing delay elements ')
    sys.stdout.flush()
    progress = max(1, len(vals) / 100)
    for vali, val in enumerate(vals):
        if vali % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        odl = [(pip2speed(pip), None) for pip in val['pips']]
        names.update(OrderedDict(odl))

        odl = [(wire2speed(wire), None) for wire in val['wires']]
        names.update(OrderedDict(odl))
    print(' done')

    # Apply transform
    orig_names = len(names)
    for k in (list(name_drop) + list(name_tr.keys())):
        if k in names:
            del names[k]
        else:
            print('WARNING: failed to remove %s' % k)
    names.update(OrderedDict([(name, None) for name in name_tr.values()]))
    print('Names tr %d => %d' % (orig_names, len(names)))

    # Make unique list
    names = list(names.keys())
    name_s2i = {}
    for namei, name in enumerate(names):
        name_s2i[name] = namei
    if verbose:
        for name in names:
            print('NAME: ', name)
        for name in name_drop:
            print('DROP: ', name)
        for l, r in name_tr.items():
            print('TR: %s => %s' % (l, r))

    # Now create a matrix with all of these delays
    # Each row needs len(names) elements
    # -2 means 2 elements present, 0 means absent
    # (could hit same pip twice)
    print('Creating delay element matrix w/ %d names' % len(names))
    Adi = [None for _i in range(len(vals))]
    for vali, val in enumerate(vals):

        def add_name(name):
            if name in name_drop:
                return
            name = name_tr.get(name, name)
            namei = name_s2i[name]
            row_di[namei] = row_di.get(namei, 0) + 1

        # Start with 0 occurances
        #row = [0 for _i in range(len(names))]
        row_di = {}

        #print('pips: ', val['pips']
        for pip in val['pips']:
            add_name(pip2speed(pip))
        for wire in val['wires']:
            add_name(wire2speed(wire))
        #A_ub.append(row)
        Adi[vali] = row_di

    return Adi, names


# TODO: load directly as Ads
# remove names_tr, names_drop
def vals2Ads(vals, speed_i2s, verbose=False):
    Adi, names = vals2Adi(vals, speed_i2s, verbose=False)
    return A_di2ds(Adi, names)


def load_Ads(speed_json_f, f_ins):

    print('Loading data')

    _speedj, speed_i2s = load_speed_json(speed_json_f)

    vals = []
    for avals in [load_timing3(f_in, name) for f_in, name in f_ins]:
        vals.extend(avals)

    Ads = vals2Ads(vals, speed_i2s)

    def mkb(val):
        return (
            val['fast_max'], val['fast_min'], val['slow_max'], val['slow_min'])

    b = [mkb(val) for val in vals]
    ico = [val['ico'] for val in vals]

    return Ads, b, ico


def run(speed_json_f, fout, f_ins, verbose=0, corner=None):
    Ads, bs, ico = load_Ads(speed_json_f, f_ins)

    fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
    for row_bs, row_ds, row_ico in zip(bs, Ads, ico):
        # XXX: consider removing ico column
        # its obsolete at this point
        if not ico:
            continue
        # like: 123 456 120 450, 1 a, 2 b
        # first column has delay corners, followed by delay element count
        items = [str(row_ico), ' '.join([str(x) for x in row_bs])]
        for k, v in sorted(row_ds.items()):
            items.append('%u %s' % (v, k))
        fout.write(','.join(items) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Convert obscure timing3.txt into more readable but roughly equivilent timing3i.csv (interconnect)'
    )

    parser.add_argument('--verbose', type=int, help='')
    # made a bulk conversion easier...keep?
    parser.add_argument(
        '--auto-name', action='store_true', help='timing3.txt => timing3i.csv')
    parser.add_argument(
        '--speed-json',
        default='build_speed/speed.json',
        help='Provides speed index to name translation')
    parser.add_argument('--out', default=None, help='Output timing3i.csv file')
    parser.add_argument('fns_in', nargs='+', help='Input timing3.txt files')
    args = parser.parse_args()
    bench = Benchmark()

    fnout = args.out
    if fnout is None:
        if args.auto_name:
            assert len(args.fns_in) == 1
            fnin = args.fns_in[0]
            fnout = fnin.replace('.txt', 'i.csv')
            assert fnout != fnin, 'Expect .txt in'
        else:
            # practically there are too many stray prints to make this work as expected
            assert 0, 'File name required'
            fnout = '/dev/stdout'
    print("Writing to %s" % fnout)
    fout = open(fnout, 'w')

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing3.txt')

    run(
        speed_json_f=open(args.speed_json, 'r'),
        fout=fout,
        f_ins=[(open(fn_in, 'r'), fn_in) for fn_in in fns_in],
        verbose=args.verbose)


if __name__ == '__main__':
    main()
