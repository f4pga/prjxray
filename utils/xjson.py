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
import sys
import json
from prjxray.xjson import pprint
from prjxray.util import OpenSafeFile

if __name__ == "__main__":
    if len(sys.argv) == 1:
        import doctest
        doctest.testmod()
    else:
        assert len(sys.argv) == 2
        with OpenSafeFile(sys.argv[1]) as f:
            d = json.load(f)
        pprint(sys.stdout, d)
