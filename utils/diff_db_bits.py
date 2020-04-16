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
import argparse
import subprocess
import tempfile
import os.path
import glob


def main():
    parser = argparse.ArgumentParser(
        description=
        "Tool for comparing database segbits outputs from two database's.")
    parser.add_argument('a_db')
    parser.add_argument('b_db')

    args = parser.parse_args()

    assert os.path.isdir(args.a_db)
    assert os.path.isdir(args.b_db)

    for a_db_in in glob.glob('{}/segbits*.db'.format(args.a_db)):
        a_db_base = os.path.basename(a_db_in)
        b_db_in = '{}/{}'.format(args.b_db, a_db_base)

        if not os.path.exists(b_db_in):
            print('{} not found!'.format(b_db_in))
            continue

        with tempfile.NamedTemporaryFile(suffix="_a_{}".format(
                a_db_base)) as a_db_out, tempfile.NamedTemporaryFile(
                    suffix="_b_{}".format(a_db_base)) as b_db_out:
            subprocess.check_call(
                "sort {}".format(a_db_in), shell=True, stdout=a_db_out)
            subprocess.check_call(
                "sort {}".format(b_db_in), shell=True, stdout=b_db_out)

            print("Comparing {}".format(a_db_base))
            subprocess.call(
                "diff -U 0 {} {}".format(a_db_out.name, b_db_out.name),
                shell=True)


if __name__ == "__main__":
    main()
