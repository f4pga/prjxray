'''
Verifies that node timing info is unique
'''

import re


def gen_nodes(fin):
    for l in fin:
        lj = {}
        l = l.strip()
        for kvs in l.split():
            name, value = kvs.split(':')
            '''
            NAME:LIOB33_SING_X0Y199/IOB_IBUF0

            IS_BAD:0
            IS_COMPLETE:1
            IS_GND:0 IS_INPUT_PIN:1 IS_OUTPUT_PIN:0 IS_PIN:1 IS_VCC:0 
            NUM_WIRES:2
            PIN_WIRE:1
            '''
            if name in ('COST_CODE', 'SPEED_CLASS'):
                value = int(value)
            lj[name] = value

        tile_type, xy, wname = re.match(
            r'(.*)_(X[0-9]*Y[0-9]*)/(.*)', lj['NAME']).groups()
        lj['tile_type'] = tile_type
        lj['xy'] = xy
        lj['wname'] = wname

        lj['l'] = l

        yield lj


def run(node_fin, verbose=0):
    refnodes = {}
    nodei = 0
    for nodei, anode in enumerate(gen_nodes(node_fin)):

        def getk(anode):
            return anode['wname']
            #return (anode['tile_type'], anode['wname'])

        if nodei % 1000 == 0:
            print 'Check node %d' % nodei
        # Existing node?
        try:
            refnode = refnodes[getk(anode)]
        except KeyError:
            # Set as reference
            refnodes[getk(anode)] = anode
            continue
        # Verify equivilence
        for k in (
                'SPEED_CLASS',
                'COST_CODE',
                'COST_CODE_NAME',
                'IS_BAD',
                'IS_COMPLETE',
                'IS_GND',
                'IS_VCC',
        ):
            if k in refnode and k in anode:

                def fail():
                    print 'Mismatch on %s' % k
                    print refnode[k], anode[k]
                    print refnode['l']
                    print anode['l']
                    #assert 0

                if k == 'SPEED_CLASS':
                    # Parameters known to effect SPEED_CLASS
                    # Verify at least one parameter is different
                    if refnode[k] != anode[k]:
                        for k2 in ('IS_PIN', 'IS_INPUT_PIN', 'IS_OUTPUT_PIN',
                                   'PIN_WIRE', 'NUM_WIRES'):
                            if refnode[k2] != anode[k2]:
                                break
                        else:
                            if 0:
                                print
                                fail()
                elif refnode[k] != anode[k]:
                    print
                    fail()
            # A key in one but not the other?
            elif k in refnode or k in anode:
                assert 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Timing fuzzer')

    parser.add_argument('--verbose', type=int, help='')
    parser.add_argument(
        'node_fn_in', default='/dev/stdin', nargs='?', help='Input file')
    args = parser.parse_args()
    run(open(args.node_fn_in, 'r'), verbose=args.verbose)
