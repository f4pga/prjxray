# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
.PHONY: all clean

all: firmware run

clean:
	rm -rf *.elf
	rm -rf *.o

firmware:
	arm-linux-gnueabihf-as -o blink.o blink.s
	arm-linux-gnueabihf-ld -o blink.elf -T blink.ld blink.o

run: blink.elf
	xsct blink.tcl
