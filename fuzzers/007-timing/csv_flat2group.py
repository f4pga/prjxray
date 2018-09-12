#!/usr/bin/env python3

from timfuz import Benchmark, loadc_Ads_bs, index_names, load_sub, run_sub_json, instances

def gen_group(fnin, sub_json, strict=False, verbose=False):
    print('Loading data')
    Ads, bs = loadc_Ads_bs([fnin], ico=True)

    print('Sub: %u rows' % len(Ads))
    iold = instances(Ads)
    names_old = index_names(Ads)
    run_sub_json(Ads, sub_json, strict=strict, verbose=verbose)
    names = index_names(Ads)
    print("Sub: %u => %u names" % (len(names_old), len(names)))
    print('Sub: %u => %u instances' % (iold, instances(Ads)))

    for row_ds, row_bs in zip(Ads, bs):
        yield row_ds, row_bs

def run(fns_in, fnout, sub_json, strict=False, verbose=False):
    with open(fnout, 'w') as fout:
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for fn_in in fns_in:
            for row_ds, row_bs in gen_group(fn_in, sub_json, strict=strict):
                row_ico = 1
                items = [str(row_ico), ' '.join([str(x) for x in row_bs])]
                for k, v in sorted(row_ds.items()):
                    items.append('%u %s' % (v, k))
                fout.write(','.join(items) + '\n')

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--strict', action='store_true', help='')
    parser.add_argument('--sub-csv', help='')
    parser.add_argument('--sub-json', required=True, help='Group substitutions to make fully ranked')
    parser.add_argument('--out', help='Output sub.json substitution result')
    parser.add_argument(
        'fns_in',
        nargs='*',
        help='timing3.txt input files')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    sub_json = load_sub(args.sub_json)

    try:
        run(args.fns_in, args.out, sub_json=sub_json, strict=args.strict, verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)

if __name__ == '__main__':
    main()
