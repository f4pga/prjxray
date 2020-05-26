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

from __future__ import print_function
import sys, re
import os
import glob
import hashlib


def bytehex(x):
    return ''.join('{:02x}'.format(x) for x in x)


def wc_for_iteration(todo_dir, fni):
    with open("%s/%u_all.txt" % (todo_dir, fni), "rb") as f:
        return sum(1 for _ in f)


def check_made_progress(todo_dir, max_iter, min_progress):
    """ Returns true if minimum progress is being made. """
    if max_iter == 1:
        return True

    prev_iteration = wc_for_iteration(todo_dir, max_iter - 1)
    cur_iteration = wc_for_iteration(todo_dir, max_iter)

    made_progress = prev_iteration - cur_iteration > min_progress
    if not made_progress:
        print(
            "Between iteration {} and iteration {} only {} pips were solved.  Terminating iteration."
            .format(max_iter - 1, max_iter, prev_iteration - cur_iteration))

    return made_progress


def run(
        todo_dir,
        min_iters=None,
        min_progress=None,
        timeout_iters=None,
        max_iters=None,
        zero_entries=None,
        zero_entries_filter=".*",
        verbose=False):
    timeout_fn = "%s/timeout" % todo_dir
    # make clean removes todo dir, but helps debugging
    if os.path.exists(timeout_fn):
        print("WARNING: removing %s" % timeout_fn)
        os.remove(timeout_fn)

    alls = glob.glob("%s/*_all.txt" % todo_dir)
    max_iter = 0
    for fn in alls:
        n = int(re.match(r".*/([0-9]*)_all.txt", fn).group(1))
        max_iter = max(max_iter, n)

    if max_iter == 0:
        print("Incomplete: no iters")
        sys.exit(1)

    verbose and print("Max iter: %u, need: %s" % (max_iter, min_iters))

    # Don't allow early termination if below min_iters
    if min_iters is not None and max_iter < min_iters:
        print("Incomplete: not enough iters")
        sys.exit(1)

    # Force early termination if at or above max_iters.
    if max_iters is not None and max_iter >= max_iters:
        print(
            "Complete: reached max iters (want %u, got %u)" %
            (max_iters, max_iter))
        sys.exit(0)

    # Mark timeout if above timeout_iters
    if timeout_iters is not None and max_iter > timeout_iters:
        print("ERROR: timeout (max %u, got %u)" % (timeout_iters, max_iter))
        with open(timeout_fn, "w") as _f:
            pass
        sys.exit(1)

    # Check if zero entries criteria is not met.
    if zero_entries:
        filt = re.compile(zero_entries_filter)
        count = 0
        fn = "%s/%u_all.txt" % (todo_dir, max_iter)
        with open(fn, 'r') as f:
            for l in f:
                if filt.search(l):
                    count += 1

        if count > 0:
            print("%s: %s lines" % (fn, count))
            print(
                "Incomplete: need zero entries (used filter: {})".format(
                    repr(zero_entries_filter)))
            sys.exit(1)
        else:
            # If there are zero entries, check if min_progress criteria is in
            # affect. If so, that becomes the new termination condition.
            if min_progress is None:
                print(
                    "No unfiltered entries, done (used filter: {})!".format(
                        repr(zero_entries_filter)))
                sys.exit(0)
            else:
                # Even if there are 0 unfiltered entries, fuzzer may still be
                # making progress with filtered entries.
                print(
                    "No unfiltered entries (used filter: {}), checking if progress is being made"
                    .format(repr(zero_entries_filter)))

    # Check if minimum progress was achieved, continue iteration if so.
    if min_progress is not None and not check_made_progress(todo_dir, max_iter,
                                                            min_progress):
        sys.exit(0)

    print("No exit criteria met, keep going!")
    sys.exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        "Check int_loop completion. Exits 0 on done, 1 if more loops are needed"
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--todo-dir', default="build/todo", help='')
    parser.add_argument(
        '--min-iters', default=None, help='Minimum total number of iterations')
    parser.add_argument(
        '--min-progress',
        default=None,
        help=
        'Minimum amount of process between iterations.  If less progress is made, terminates immediately.'
    )
    parser.add_argument(
        '--timeout-iters',
        default=None,
        help='Max number of entries before creating todo/timeout')
    parser.add_argument(
        '--max-iters',
        default=None,
        help='Max number of entries before declaring success')
    parser.add_argument(
        '--zero-entries',
        action="store_true",
        help='Must be no unsolved entries in latest')
    parser.add_argument(
        '--zero-entries-filter',
        default=".*",
        help=
        'When zero-entries is supplied, this filter is used to filter pips used for counting against zero entries termination condition.'
    )
    args = parser.parse_args()

    def zint(x):
        return None if x is None else int(x)

    run(
        todo_dir=args.todo_dir,
        min_iters=zint(args.min_iters),
        min_progress=zint(args.min_progress),
        timeout_iters=zint(args.timeout_iters),
        max_iters=zint(args.max_iters),
        zero_entries=args.zero_entries,
        zero_entries_filter=args.zero_entries_filter,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
