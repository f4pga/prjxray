#!/usr/bin/env python3

import sys
import os
import time
import json


def run_types(tilej, verbose=False):
    def process(etype):
        # dict[model] = set((tile, wire/pip))
        zeros = {}
        print('Processing %s' % etype)
        # Index delay models by type, recording where they occured
        for tilek, tilev in tilej['tiles'].items():
            for ename, emodel in tilev[etype].items():
                if emodel.find('ZERO') >= 0:
                    zeros.setdefault(emodel, set()).add((tilek, ename))
        # Print out delay model instances
        print('%s ZERO types: %u, %s' % (etype, len(zeros), zeros.keys()))
        print(
            '%s ZERO instances: %u' %
            (etype, sum([len(x) for x in zeros.values()])))
        for model in sorted(zeros.keys()):
            modelv = zeros[model]
            print('Model: %s' % model)
            for tile_name, element_name in sorted(list(modelv)):
                print('  %s: %s' % (tile_name, element_name))

    process('wires')
    print('')
    process('pips')


def run_prefix(tilej, verbose=False):
    def process(etype):
        prefixes = set()
        print('Processing %s' % etype)
        # Index delay models by type, recording where they occured
        for tilek, tilev in tilej['tiles'].items():
            for ename, emodel in tilev[etype].items():
                prefix = emodel.split('_')[0]
                prefixes.add(prefix)
        print('%s prefixes: %u' % (etype, len(prefixes)))
        for prefix in sorted(prefixes):
            print('  %s' % prefix)

    process('wires')
    print('')
    process('pips')


def run(fnin, verbose=False):
    tilej = json.load((open(fnin, 'r')))
    run_types(tilej)
    print('')
    print('')
    run_prefix(tilej)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Solve timing solution')
    parser.add_argument(
        'fnin',
        default="../timgrid/build/timgrid-s.json",
        nargs='?',
        help='input timgrid JSON')
    args = parser.parse_args()

    run(args.fnin, verbose=False)


if __name__ == '__main__':
    main()
