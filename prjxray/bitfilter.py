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

from prjxray.util import OpenSafeFile

class Bitfilter(object):
    def __init__(
            self, frames_to_include=None, frames_to_exclude=[],
            bits_to_exclude=[]):
        self.frames_to_include = frames_to_include
        self.frames_to_exclude = frames_to_exclude
        self.bits_to_exclude = bits_to_exclude

    def filter(self, frame, bit):
        if self.frames_to_include is not None:
            if frame in self.frames_to_include:
                return True

        if frame in self.frames_to_exclude:
            return False

        if (frame, bit) in self.bits_to_exclude:
            return False

        return True


BITFILTERS = {
    ('artix7', 'INT'):
    Bitfilter(
        frames_to_exclude=[
            30,
            31,
        ],
        bits_to_exclude=[
            #
            (0, 36)
        ]),
}


def get_bitfilter(part, tile):
    """ Returns bitfilter for specified part and tile.

    Either returns bitfilter to specified part and tile type, or the default
    bitfilter, which includes all bits.
    """
    key = (part, tile)
    if key in BITFILTERS:
        return BITFILTERS[key].filter
    else:
        return None
