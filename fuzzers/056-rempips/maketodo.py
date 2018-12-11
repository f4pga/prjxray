#!/usr/bin/env python3

import os, re, sys
from prjxray import util


def maketodo(pipfile, dbfile, verbose=False):
    '''Print name of all pips in pipfile but not dbfile'''
    todos = set()
    with open(pipfile, "r") as f:
        for line in f:
            line = line.split()
            todos.add(line[0])
    verbose and print(
        '%s: %u entries' % (pipfile, len(todos)), file=sys.stderr)
    # Support generate without existing DB
    if os.path.exists(dbfile):
        with open(dbfile, "r") as f:
            for line in f:
                line = line.split()
                pip = line[0]
                todos.remove(pip)
    verbose and print(
        'Remove %s: %u entries' % (dbfile, len(todos)), file=sys.stderr)
    drops = 0
    lines = 0
    for line in todos:
        if line.endswith(".VCC_WIRE"):
            drops += 1
            continue
        print(line)
        lines += 1
    verbose and print(
        'Print %u entries w/ %u drops' % (lines, drops), file=sys.stderr)


def run(build_dir):
    db_dir = "%s/%s" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"))

    maketodo("%s/pips_int_l.txt" % build_dir, "%s/segbits_int_l.db" % db_dir)
    maketodo("%s/pips_int_r.txt" % build_dir, "%s/segbits_int_r.db" % db_dir)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Print list of known but unsolved PIPs")

    parser.add_argument('--build-dir', default="build", help='')
    args = parser.parse_args()

    run(build_dir=args.build_dir)


if __name__ == '__main__':
    main()
