#!/usr/bin/env python3

from timfuz import Benchmark, simplify_rows, loadc_Ads_b
import glob


def run(fout, fns_in, corner, verbose=0):
    Ads, b = loadc_Ads_b(fns_in, corner, ico=True)
    Ads, b = simplify_rows(Ads, b, corner=corner)

    fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
    for row_b, row_ds in zip(b, Ads):
        # write in same format, but just stick to this corner
        out_b = [str(row_b) for _i in range(4)]
        ico = '1'
        items = [ico, ' '.join(out_b)]

        for k, v in sorted(row_ds.items()):
            items.append('%u %s' % (v, k))
        fout.write(','.join(items) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Create a .csv with a single process corner')

    parser.add_argument('--verbose', type=int, help='')
    parser.add_argument(
        '--auto-name', action='store_true', help='timing3.csv => timing3c.csv')
    parser.add_argument('--out', default=None, help='Output csv')
    parser.add_argument('--corner', help='Output csv')
    parser.add_argument('fns_in', nargs='+', help='timing3.csv input files')
    args = parser.parse_args()
    bench = Benchmark()

    fnout = args.out
    if fnout is None:
        if args.auto_name:
            assert len(args.fns_in) == 1
            fnin = args.fns_in[0]
            fnout = fnin.replace('timing3.csv', 'timing3c.csv')
            assert fnout != fnin, 'Expect timing3.csv in'
        else:
            fnout = '/dev/stdout'
    print("Writing to %s" % fnout)
    fout = open(fnout, 'w')

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing3.csv')

    run(fout=fout, fns_in=fns_in, corner=args.corner, verbose=args.verbose)


if __name__ == '__main__':
    main()
