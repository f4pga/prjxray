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
'''
Script for adding the IO Banks information to the Part's generated JSON.
'''
import argparse
import json


def main(argv):
    with open(args.part_json) as json_file, open(
            args.iobanks_info) as iobanks_info:
        part_data = json.load(json_file)
        json_file.close()
        iobank_data = dict()
        for iobank in iobanks_info:
            iobank = iobank.strip()
            bank, coordinates = iobank.split(",")
            iobank_data[bank] = coordinates
        iobanks_info.close()
        if len(iobank_data) > 0:
            part_data["iobanks"] = iobank_data
        print(json.dumps(part_data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--part_json', help='Input json')
    parser.add_argument('--iobanks_info', help='Input IO Banks info file')
    args = parser.parse_args()
    main(args)
