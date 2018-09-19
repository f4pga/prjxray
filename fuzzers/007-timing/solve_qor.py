#!/usr/bin/env python3

from timfuz import Benchmark, load_sub, load_bounds, loadc_Ads_b
import numpy as np


def run(fns_in, corner, bounds_csv, verbose=False):
    print('Loading data')
    Ads, borig = loadc_Ads_b(fns_in, corner, ico=True)

    bounds = load_bounds(bounds_csv, corner)
    # verify is flattened
    for k in bounds.keys():
        assert 'GROUP_' not in k, 'Must operate on flattened bounds'

    # compute our timing model delay at the given corner
    bgots = []
    for row_ds in Ads:
        delays = [n * bounds[x] for x, n in row_ds.items()]
        bgots.append(sum(delays))

    ses = (np.asarray(bgots) - np.asarray(borig))**2
    mse = (ses).mean(axis=None)
    print('MSE aggregate: %0.1f' % mse)
    print('Min SE: %0.1f' % min(ses))
    print('Max SE: %0.1f' % max(ses))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Report a timing fit score')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--corner', required=True, default="slow_max", help='')
    parser.add_argument(
        '--bounds-csv',
        required=True,
        help='Previous solve result starting point')
    parser.add_argument('fns_in', nargs='+', help='timing3.csv input files')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing3.csv')

    try:
        run(
            fns_in=fns_in,
            corner=args.corner,
            bounds_csv=args.bounds_csv,
            verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)


if __name__ == '__main__':
    main()
