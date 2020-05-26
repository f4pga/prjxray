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
""" Generates a missing feature/bit report for LiteX design.

This script is fairly fragile, because it depends on the specific observation
that all of the remaining bits appear to either belong to HCLK_IOI or IOI3
tiles.  A more general version of this script could be created, but that was
not the point of this script.

"""
from fasm import parse_fasm_filename


def main():
    fasm_file = 'top.fasm'
    fasm_model = list(parse_fasm_filename(fasm_file))

    unknown_bits = {
        'HCLK_IOI': {},
        'IOI3': {},
    }

    total_unknown = 0
    for l in fasm_model:
        if l.annotations is None:
            continue

        annotations = {}
        for annotation in l.annotations:
            annotations[annotation.name] = annotation.value

        if 'unknown_bit' not in annotations:
            continue

        total_unknown += 1

        frame, word, bit = annotations['unknown_bit'].split('_')

        frame = int(frame, 16)
        word = int(word)
        bit = int(bit)

        frame_offset = frame % 0x80
        base_frame = frame - frame_offset

        # All remaining LiteX bits appear to be in this one IO bank, so limit
        # the tool this this one IO bank.
        assert base_frame == 0x00401580, hex(frame)

        SIZE = 4
        INITIAL_OFFSET = -2

        if word == 50:
            group = 'HCLK_IOI'
            offset = 45
        elif word < 50:
            group = 'IOI3'
            offset = ((word - INITIAL_OFFSET) // SIZE) * SIZE + INITIAL_OFFSET
        else:
            group = 'IOI3'
            word -= 1
            offset = ((word - INITIAL_OFFSET) // SIZE) * SIZE + INITIAL_OFFSET
            offset += 1
            word += 1

        bit = '{}_{:02d}'.format(
            frame_offset,
            (word - offset) * 32 + bit,
        )

        if bit not in unknown_bits[group]:
            unknown_bits[group][bit] = 0
        unknown_bits[group][bit] += 1

    print('Total unknown bits: {}'.format(total_unknown))
    for group in unknown_bits:
        print('Group {} (count = {}):'.format(group, len(unknown_bits[group])))
        for bit in sorted(unknown_bits[group]):
            print('  {} (count = {})'.format(bit, unknown_bits[group][bit]))


if __name__ == "__main__":
    main()
