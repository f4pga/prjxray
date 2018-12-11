#!/usr/bin/env python3

import sys, re
import os
import glob
import hashlib


# len(txt.split("\n"))) is off by 1
def wc(fn):
    i = 0
    with open(fn) as f:
        for i, _l in enumerate(f, 1):
            pass
    return i


def bytehex(x):
    return ''.join('{:02x}'.format(x) for x in x)


def calc_stable_iters(todo_dir, max_iter):
    m5s = []
    wcs = []
    m5_last = None
    stablen = 0
    for fni in range(1, max_iter + 1, 1):
        fn = "%s/%u_all.txt" % (todo_dir, fni)
        txt = open(fn, "r").read()
        m5 = hashlib.md5(txt.encode("ascii")).hexdigest()

        m5s.append(m5)
        wc_this = wc(fn)
        wcs.append(wc_this)

        if m5_last == m5:
            stablen += 1
        else:
            stablen = 1

        print(
            "% 4u %s % 6u lines % 6u stable" %
            (fni, m5[0:8], wc_this, stablen))

        m5_last = m5

    return stablen


def run(
        todo_dir,
        min_iters=None,
        stable_iters=None,
        timeout_iters=None,
        zero_entries=None,
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

    fn = "%s/%u_all.txt" % (todo_dir, max_iter)
    txt = open(fn, "r").read()
    nbytes = len(txt)

    stablen = calc_stable_iters(todo_dir, max_iter)

    if min_iters is not None and max_iter < min_iters:
        print("Incomplete: not enough iters")
        sys.exit(1)

    if timeout_iters is not None and max_iter > timeout_iters:
        print("ERROR: timeout (max %u, got %u)" % (timeout_iters, max_iter))
        with open(timeout_fn, "w") as _f:
            pass
        sys.exit(1)

    if zero_entries and nbytes:
        print("%s: %u bytes, %s lines" % (fn, nbytes, wc(fn)))
        print("Incomplete: need zero entries")
        sys.exit(1)

    if stable_iters:
        if stablen < stable_iters:
            print(
                "Incomplete: insufficient stable iters (got %s, need %s)" %
                (stablen, stable_iters))
            sys.exit(1)

    print("Complete!")
    sys.exit(0)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        "Check int_loop completion. Exits 0 on done, 1 if more loops are needed"
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--todo-dir', default="todo", help='')
    parser.add_argument(
        '--min-iters', default=None, help='Minimum total number of iterations')
    parser.add_argument(
        '--stable-iters',
        default=None,
        help='Number of iterations without any change')
    parser.add_argument(
        '--timeout-iters',
        default=None,
        help='Max number of entries before creating todo/timeout')
    parser.add_argument(
        '--zero-entries',
        action="store_true",
        help='Must be no unsolved entries in latest')
    args = parser.parse_args()

    def zint(x):
        return None if x is None else int(x)

    run(
        args.todo_dir,
        zint(args.min_iters),
        zint(args.stable_iters),
        zint(args.timeout_iters),
        args.zero_entries,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
