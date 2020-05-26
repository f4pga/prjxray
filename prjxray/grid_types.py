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
from collections import namedtuple
import enum


class BlockType(enum.Enum):
    # Frames describing CLB features, interconnect, clocks and IOs.
    CLB_IO_CLK = 'CLB_IO_CLK'

    # Frames describing block RAM initialization.
    BLOCK_RAM = 'BLOCK_RAM'


GridLoc = namedtuple('GridLoc', 'grid_x grid_y')
ClockRegion = namedtuple('ClockRegion', 'name x y')
GridInfo = namedtuple(
    'GridInfo',
    'bits sites prohibited_sites tile_type pin_functions clock_region')
BitAlias = namedtuple('BitAlias', 'tile_type start_offset sites')
Bits = namedtuple('Bits', 'base_address frames offset words alias')
BitsInfo = namedtuple('BitsInfo', 'block_type tile bits')
