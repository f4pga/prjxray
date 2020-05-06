# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
connect
targets -set -nocase -filter {name =~ "ARM* #0"}
rst -system
dow blink.elf
con
