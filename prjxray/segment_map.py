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
from intervaltree import IntervalTree, Interval
from prjxray import bitstream


class SegmentMap(object):
    def __init__(self, grid):
        self.segment_tree = IntervalTree()

        for bits_info in grid.iter_all_frames():
            self.segment_tree.add(
                Interval(
                    begin=bits_info.bits.base_address,
                    end=bits_info.bits.base_address + bits_info.bits.frames,
                    data=bits_info,
                ))

    def segment_info_for_frame(self, frame):
        """ Return all bits info that match frame address. """
        for frame in self.segment_tree[frame]:
            yield frame.data
