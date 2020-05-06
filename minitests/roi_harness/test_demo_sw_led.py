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

import unittest
import demo_sw_led


class TestStringMethods(unittest.TestCase):
    def test_all(self):
        for i in range(8):
            print()
            print()
            print()
            print(i)
            demo_sw_led.run('out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev', i, i)


if __name__ == '__main__':
    unittest.main()
