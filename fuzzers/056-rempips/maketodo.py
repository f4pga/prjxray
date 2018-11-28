#!/usr/bin/env python3

import os, re, sys
from prjxray import util


def maketodo(pipfile, dbfile, strict=True):
    '''Print name of all pips in pipfile but not dbfile'''
    todos = set()
    with open(pipfile, "r") as f:
        for line in f:
            line = line.split()
            todos.add(line[0])
    print('%s: %u entries' % (pipfile, len(todos)), file=sys.stderr)
    # Support generate without existing DB
    if os.path.exists(dbfile) or strict:
        with open(dbfile, "r") as f:
            for line in f:
                line = line.split()
                pip = line[0]
                try:
                    todos.remove(pip)
                except KeyError:
                    # DB (incorrectly) had multiple entries
                    # Workaround for testing on old DB revision
                    if strict:
                        raise
                    print(
                        'WARNING: failed to remove pip %s' % pip,
                        file=sys.stderr)
    print('Remove %s: %u entries' % (dbfile, len(todos)), file=sys.stderr)
    drops = 0
    lines = 0
    for line in todos:
        if line.endswith(".VCC_WIRE"):
            drops += 1
            continue
        print(line)
        lines += 1
    print('Print %u entries w/ %u drops' % (lines, drops), file=sys.stderr)


def run(strict=True):
    maketodo(
        "build/pips_int_l.txt",
        "%s/%s/segbits_int_l.db" %
        (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")),
        strict=strict)
    maketodo(
        "build/pips_int_r.txt",
        "%s/%s/segbits_int_r.db" %
        (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")),
        strict=strict)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Print list of known but unsolved PIPs")

    # util.db_root_arg(parser)
    parser.add_argument('--no-strict', action='store_true', help='')
    args = parser.parse_args()

    run(strict=not args.no_strict)


if __name__ == '__main__':
    main()
