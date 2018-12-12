#!/usr/bin/env python3

import os, re
import sys
from prjxray import util


def noprefix(tag):
    n = tag.find('.')
    assert n > 0
    return tag[n + 1:]


def getprefix(tag):
    n = tag.find('.')
    assert n > 0
    return tag[0:n]


def load_pipfile(pipfile):
    '''Returns a set of tags containing real tile type prefixes (ex: INT_L)'''
    todos = set()
    tile_type = None
    with open(pipfile, "r") as f:
        # INT_L.WW2BEG0.SR1BEG_S0
        for line in f:
            tag, _bits, mode = util.parse_db_line(line)
            # Only count resolved entries
            if mode:
                continue

            prefix_line = getprefix(tag)
            if tile_type is None:
                tile_type = prefix_line
            else:
                assert tile_type == prefix_line
            todos.add(tag)
    return todos, tile_type


def maketodo(pipfile, dbfile, intre, not_endswith=None, verbose=False):
    '''
    db files start with INT., but pipfile lines start with INT_L
    Normalize by removing before the first dot
    050-intpips doesn't care about contents, but most fuzzers use the tile type prefix
    '''

    todos, tile_type = load_pipfile(pipfile)
    verbose and print('%s: %u entries' % (pipfile, len(todos)))
    verbose and print("pipfile todo sample: %s" % list(todos)[0])

    # Allow against empty db
    if os.path.exists(dbfile):
        verbose and print("Loading %s" % dbfile)
        with open(dbfile, "r") as f:
            # INT.BYP_ALT0.BYP_BOUNCE_N3_3 !22_07 !23_07 !25_07 21_07 24_07
            for line in f:
                line = line.split()
                tag = tile_type + '.' + noprefix(line[0])
                # bipips works on a subset
                if tag in todos:
                    todos.remove(tag)
                else:
                    verbose and print(
                        "WARNING: couldnt remove %s (line %s)" % (tag, line))
    else:
        verbose and print("WARNING: dbfile doesnt exist: %s" % dbfile)
    verbose and print('Remove %s: %u entries' % (dbfile, len(todos)))
    drops = 0
    lines = 0
    for line in todos:
        if re.match(intre, line) and (not_endswith is None
                                      or not line.endswith(not_endswith)):
            print(line)
        else:
            drops += 1
        lines += 1
    verbose and print('Print %u entries w/ %u drops' % (lines, drops))


def run(build_dir, db_dir, intre, pip_type, not_endswith=None, verbose=False):
    if db_dir is None:
        db_dir = "%s/%s" % (
            os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"))

    assert intre, "RE is required"
    maketodo(
        "%s/%s_l.txt" % (build_dir, pip_type),
        "%s/segbits_int_l.db" % db_dir,
        intre,
        not_endswith,
        verbose=verbose)
    maketodo(
        "%s/%s_r.txt" % (build_dir, pip_type),
        "%s/segbits_int_r.db" % db_dir,
        intre,
        not_endswith,
        verbose=verbose)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Print list of known but unsolved PIPs")

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--build-dir', default="build", help='')
    parser.add_argument('--db-dir', default=None, help='')
    parser.add_argument('--re', required=True, help='')
    parser.add_argument('--pip-type', default="pips_int", help='')
    parser.add_argument(
        '--not-endswith', help='Drop lines if they end with this')
    args = parser.parse_args()

    run(
        build_dir=args.build_dir,
        db_dir=args.db_dir,
        intre=args.re,
        pip_type=args.pip_type,
        not_endswith=args.not_endswith,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
