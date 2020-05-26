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
import pyjson5
import simplejson
import sys


def main():
    simplejson.dump(pyjson5.load(sys.stdin), sys.stdout, indent=2)


if __name__ == "__main__":
    main()
