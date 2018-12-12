#!/usr/bin/env python3

import os, re
import sys


def maketodo(pipfile, dbfile, intre, not_endswith=None, verbose=False):
    todos = set()
    with open(pipfile, "r") as f:
        for line in f:
            line = line.split()
            todos.add(line[0])
    verbose and print(
        '%s: %u entries' % (pipfile, len(todos)), file=sys.stderr)
    # Allow against empty db
    if os.path.exists(dbfile):
        with open(dbfile, "r") as f:
            for line in f:
                line = line.split()
                # bipips works on a subset
                if line[0] in todos:
                    todos.remove(line[0])
    verbose and print(
        'Remove %s: %u entries' % (dbfile, len(todos)), file=sys.stderr)
    drops = 0
    lines = 0
    for line in todos:
        if re.match(intre, line) and (not_endswith is None
                                      or not line.endswith(not_endswith)):
            print(line)
        else:
            drops += 1
        lines += 1
    verbose and print(
        'Print %u entries w/ %u drops' % (lines, drops), file=sys.stderr)


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
        not_endswith=args.not_endswith)


if __name__ == '__main__':
    main()
