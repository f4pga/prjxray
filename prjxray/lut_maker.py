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
class LutMaker(object):
    def __init__(self):
        self.input_lut_idx = 0
        self.output_lut_idx = 0
        self.lut_input_idx = 0

    def get_next_input_net(self):
        net = 'lut_{}_i[{}]'.format(self.input_lut_idx, self.lut_input_idx)

        self.lut_input_idx += 1
        if self.lut_input_idx > 5:
            self.lut_input_idx = 0
            self.input_lut_idx += 1

        return net

    def get_next_output_net(self):
        net = 'lut_{}_o'.format(self.output_lut_idx)
        self.output_lut_idx += 1
        return net

    def create_wires_and_luts(self):
        if self.output_lut_idx > self.input_lut_idx:
            nluts = self.output_lut_idx
        else:
            nluts = self.input_lut_idx
            if self.lut_input_idx > 0:
                nluts += 1

        for lut in range(nluts):
            yield """
            wire [5:0] lut_{lut}_i;
            wire lut_{lut}_o;

            (* KEEP, DONT_TOUCH *)
            LUT6 lut_{lut} (
                .I0(lut_{lut}_i[0]),
                .I1(lut_{lut}_i[1]),
                .I2(lut_{lut}_i[2]),
                .I3(lut_{lut}_i[3]),
                .I4(lut_{lut}_i[4]),
                .I5(lut_{lut}_i[5]),
                .O(lut_{lut}_o)
            );
            """.format(lut=lut)
