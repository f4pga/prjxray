#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os, re
from prjxray import util


def noprefix(tag):
    n = tag.find('.')
    assert n > 0
    return tag[n + 1:]


def getprefix(tag):
    n = tag.find('.')
    assert n > 0
    return tag[0:n]


def load_pipfile(pipfile, verbose=False):
    '''Returns a set of tags containing real tile type prefixes (ex: INT_L)'''
    todos = set()
    tile_type = None
    with open(pipfile, "r") as f:
        # INT_L.WW2BEG0.SR1BEG_S0
        for line in f:
            tag = line.strip().split(' ')[0]
            prefix_line = getprefix(tag)
            if tile_type is None:
                tile_type = prefix_line
            else:
                assert tile_type == prefix_line
            todos.add(tag)
    return todos, tile_type


def balance_todo_list(
        pipfile,
        todos,
        balance_wire_re,
        balance_wire_direction,
        balance_wire_cnt,
        verbose=False):
    """Balance the contents of the todo list

    Todo list balancing allows to specify the name, direction and minimal number of
    occurrences of a PIP wire in the final todo list.
    The mechanism should be used in cases where a fuzzer times out because of an
    unsolvable todo list, i.e. the netlist and resulting segdata generated from an
    iteration keep segmatch from properly disambiguating the bits for some features.

    When the balance wire name regexp is specified it's guaranteed that all PIPs
    with matching wire name (whether we want to match a src or dst wire has to be
    specified with the --balance-wire-direction switch) will have at least the number
    of entries specified with the --balance-wire-cnt switch in the final todo list.
    """
    orig_todos, tile_type = load_pipfile(pipfile, verbose=verbose)
    if balance_wire_re is not None:
        todo_wires = {}
        verbose and print("Start balancing the TODO list")
        for todo in todos:
            tile_type, dst, src = todo.split(".")
            wire = src
            other_wire = dst
            if balance_wire_direction not in "src":
                wire = dst
                other_wire = src
            balance_wire_match = re.match(balance_wire_re, wire)
            if balance_wire_match is None:
                continue
            if wire not in todo_wires:
                todo_wires[wire] = set()
            todo_wires[wire].add(other_wire)
        for wire, other_wires in todo_wires.items():
            if len(other_wires) >= balance_wire_cnt:
                continue
            else:
                for todo in orig_todos:
                    tile_type, dst, src = todo.split(".")
                    if balance_wire_direction in "src":
                        if wire in src and dst not in todo_wires[wire]:
                            todo_wires[wire].add(dst)
                    else:
                        if wire in dst and src not in todo_wires[wire]:
                            todo_wires[wire].add(src)
                    if len(todo_wires[wire]) == balance_wire_cnt:
                        break
        for wire, other_wires in todo_wires.items():
            if len(other_wires) < balance_wire_cnt:
                verbose and print(
                    "Warning: failed to balance the todo list for wire {}, there are only {} PIPs which meet the requirement: {}"
                    .format(wire, len(other_wires), other_wires))
            for other_wire in other_wires:
                line = tile_type + "."
                if balance_wire_direction in "src":
                    line += other_wire + "." + wire
                else:
                    line += wire + "." + other_wire
                verbose and print("Adding {}".format(line))
                todos.add(line)
        verbose and print("Finished balancing the TODO list")


def maketodo(
        pipfile,
        dbfile,
        intre,
        exclude_re=None,
        balance_wire_re=None,
        balance_wire_direction=None,
        balance_wire_cnt=None,
        not_endswith=None,
        verbose=False):
    '''
    db files start with INT., but pipfile lines start with INT_L
    Normalize by removing before the first dot
    050-intpips doesn't care about contents, but most fuzzers use the tile type prefix
    '''

    todos, tile_type = load_pipfile(pipfile, verbose=verbose)
    verbose and print('%s: %u entries' % (pipfile, len(todos)))
    if not todos:
        verbose and print('%s: %u entries, done!' % (pipfile, len(todos)))
        return

    verbose and print("pipfile todo sample: %s" % list(todos)[0])

    if 0 and verbose:
        print("TODOs")
        for todo in sorted(list(todos)):
            print('  %s' % todo)

    verbose and print('Pre db %s: %u entries' % (dbfile, len(todos)))
    # Allow against empty db
    if os.path.exists(dbfile):
        verbose and print("Loading %s" % dbfile)
        with open(dbfile, "r") as f:
            # INT.BYP_ALT0.BYP_BOUNCE_N3_3 !22_07 !23_07 !25_07 21_07 24_07
            for line in f:
                tag, _bits, mode, _ = util.parse_db_line(line.strip())
                # Only count resolved entries
                if mode:
                    continue
                # INT.BLAH => INT_L.BLAH
                tag = tile_type + '.' + noprefix(tag)

                # bipips works on a subset
                if tag in todos:
                    todos.remove(tag)
                else:
                    verbose and print(
                        "WARNING: couldnt remove %s (line %s)" %
                        (tag, line.strip()))
    else:
        verbose and print("WARNING: dbfile doesnt exist: %s" % dbfile)
    verbose and print('Post db %s: %u entries' % (dbfile, len(todos)))

    drops = 0
    lines = 0
    filtered_todos = set()
    for line in todos:
        include = re.match(intre, line) is not None

        if include and not_endswith is not None:
            include = not line.endswith(not_endswith)

        if include and exclude_re is not None:
            include = re.match(exclude_re, line) is None

        if include:
            filtered_todos.add(line)
        else:
            drops += 1
        lines += 1
    verbose and print('Print %u entries w/ %u drops' % (lines, drops))

    balance_todo_list(
        pipfile, filtered_todos, balance_wire_re, balance_wire_direction,
        balance_wire_cnt, verbose)
    for todo in filtered_todos:
        print(todo)


def run(
        build_dir,
        db_dir,
        pip_dir,
        intre,
        sides,
        l,
        r,
        pip_type,
        seg_type,
        exclude_re=None,
        balance_wire_re=None,
        balance_wire_direction=None,
        balance_wire_cnt=None,
        not_endswith=None,
        verbose=False):
    if db_dir is None:
        db_dir = "%s/%s" % (
            os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"))

    if pip_dir is None:
        pip_dir = "%s/piplist/build/%s" % (
            os.getenv("XRAY_FUZZERS_DIR"), pip_type)

    assert intre, "RE is required"

    for side in sides:
        if side == "l" and not l:
            continue

        if side == "r" and not r:
            continue

        if side == "xl":
            segfile = "l{}".format(seg_type)
            pipfile = "l{}".format(pip_type)
        elif side == "xr":
            segfile = "r{}".format(seg_type)
            pipfile = "r{}".format(pip_type)
        elif side != "":
            segfile = "{}_{}".format(seg_type, side)
            pipfile = "{}_{}".format(pip_type, side)
        else:
            segfile = "{}".format(seg_type)
            pipfile = "{}".format(pip_type)

        maketodo(
            "%s/%s.txt" % (pip_dir, pipfile),
            "%s/segbits_%s.db" % (db_dir, segfile),
            intre,
            exclude_re=exclude_re,
            balance_wire_re=balance_wire_re,
            balance_wire_direction=balance_wire_direction,
            balance_wire_cnt=balance_wire_cnt,
            not_endswith=not_endswith,
            verbose=verbose)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Print list of known but unsolved PIPs")

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--build-dir', default="build", help='')
    parser.add_argument('--db-dir', default=None, help='')
    parser.add_argument('--pip-dir', default=None, help='')
    parser.add_argument('--re', required=True, help='')
    parser.add_argument('--exclude-re', required=False, default=None, help='')
    parser.add_argument(
        '--balance-wire-re', required=False, default=None, help='')
    parser.add_argument(
        '--balance-wire-direction', required=False, default="src", help='')
    parser.add_argument(
        '--balance-wire-cnt', required=False, default="1", help='')
    parser.add_argument(
        '--balance-re-wire', required=False, default="src", help='')
    parser.add_argument('--pip-type', default="pips_int", help='')
    parser.add_argument('--seg-type', default="int", help='')
    parser.add_argument('--sides', default="l,r", help='')
    util.add_bool_arg(parser, '--l', default=True, help='')
    util.add_bool_arg(parser, '--r', default=True, help='')
    parser.add_argument(
        '--not-endswith', help='Drop lines if they end with this')
    args = parser.parse_args()

    run(
        build_dir=args.build_dir,
        db_dir=args.db_dir,
        pip_dir=args.pip_dir,
        intre=args.re,
        exclude_re=args.exclude_re,
        balance_wire_re=args.balance_wire_re,
        balance_wire_direction=args.balance_wire_direction,
        balance_wire_cnt=int(args.balance_wire_cnt),
        sides=args.sides.split(','),
        l=args.l,
        r=args.r,
        pip_type=args.pip_type,
        seg_type=args.seg_type,
        not_endswith=args.not_endswith,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
