#!/usr/bin/env python3

from timfuz import Benchmark
import json


def write_state(state, fout):
    j = {
        'names': dict([(x, None) for x in state.names]),
        'drop_names': list(state.drop_names),
        'base_names': list(state.base_names),
        'subs': dict([(name, values) for name, values in state.subs.items()]),
        'pivots': state.pivots,
    }
    json.dump(j, fout, sort_keys=True, indent=4, separators=(',', ': '))


def gen_rows(fn_ins):
    for fn_in in fn_ins:
        try:
            print('Loading %s' % fn_in)
            j = json.load(open(fn_in, 'r'))

            group0 = list(j['subs'].values())[0]
            value0 = list(group0.values())[0]
            if type(value0) is float:
                print("WARNING: skipping old format JSON")
                continue
            else:
                print("Value OK")

            for sub in j['subs'].values():
                row_ds = {}
                # TODO: convert to gcd
                # den may not always be 0
                # lazy solution...just multiply out all the fractions
                n = 1
                for _var, (_num, den) in sub.items():
                    n *= den

                for var, (num, den) in sub.items():
                    num2 = n * num
                    assert num2 % den == 0
                    row_ds[var] = num2 / den
                yield row_ds
        except:
            print("Error processing %s" % fn_in)
            raise


def run(fnout, fn_ins, verbose=0):
    print('Loading data')

    with open(fnout, 'w') as fout:
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for row_ds in gen_rows(fn_ins):
            ico = '1'
            out_b = [1e9, 1e9, 1e9, 1e9]
            items = [ico, ' '.join(['%u' % x for x in out_b])]

            for k, v in sorted(row_ds.items()):
                items.append('%i %s' % (v, k))
            fout.write(','.join(items) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Convert substitution groups into .csv to allow incremental rref results'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--out', help='Output csv')
    parser.add_argument('fns_in', nargs='+', help='sub.json input files')
    args = parser.parse_args()
    bench = Benchmark()

    fns_in = args.fns_in

    try:
        run(fnout=args.out, fn_ins=args.fns_in, verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)


if __name__ == '__main__':
    main()
