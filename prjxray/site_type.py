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
""" Description of a site type """
from collections import namedtuple
import enum


class SitePinDirection(enum.Enum):
    IN = "IN"
    OUT = "OUT"
    INOUT = "INOUT"


SiteTypePin = namedtuple('SiteTypePin', 'name direction')


class SiteType(object):
    def __init__(self, site_type):
        self.type = site_type['type']
        self.site_pins = {}
        for site_pin, site_pin_info in site_type['site_pins'].items():
            self.site_pins[site_pin] = SiteTypePin(
                name=site_pin,
                direction=SitePinDirection(site_pin_info['direction']),
            )

    def get_site_pins(self):
        return self.site_pins.keys()

    def get_site_pin(self, site_pin):
        return self.site_pins[site_pin]
