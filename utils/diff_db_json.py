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
        "Tool for comparing database JSON outputs from two database's.")
    parser.add_argument('a_db')
    parser.add_argument('b_db')

    args = parser.parse_args()

    assert os.path.isdir(args.a_db)
    assert os.path.isdir(args.b_db)

    for a_json_in in glob.glob('{}/*.json'.format(args.a_db)):
        a_json_base = os.path.basename(a_json_in)
        b_json_in = '{}/{}'.format(args.b_db, a_json_base)

        if not os.path.exists(b_json_in):
            print('{} not found!'.format(b_json_in))
            continue

        with tempfile.NamedTemporaryFile(suffix="_a_{}".format(
                a_json_base)) as a_json_out, tempfile.NamedTemporaryFile(
                    suffix="_b_{}".format(a_json_base)) as b_json_out:
            subprocess.check_call(
                "python3 -m utils.xjson {}".format(a_json_in),
                shell=True,
                stdout=a_json_out)
            subprocess.check_call(
                "python3 -m utils.xjson {}".format(b_json_in),
                shell=True,
                stdout=b_json_out)

            print("Comparing {}".format(a_json_base))
            subprocess.call(
                "diff -U 10 {} {}".format(a_json_out.name, b_json_out.name),
                shell=True)


if __name__ == "__main__":
    main()
