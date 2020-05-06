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

# This file is Copyright (c) 2015-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.platforms import arty
from litex.build.xilinx import VivadoProgrammer
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.init import get_sdram_phy_py_header
from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys4x = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200 = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset"))
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys4x, 4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200, 200e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)


# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCSDRAM):
    def __init__(self):
        platform = arty.Platform()
        sys_clk_freq = int(50e6)

        # SoCSDRAM ---------------------------------------------------------------------------------
        SoCSDRAM.__init__(
            self,
            platform,
            clk_freq=sys_clk_freq,
            ident="Minimal Arty DDR3 Design for tests with Project X-Ray",
            ident_version=True,
            cpu_type=None,
            l2_size=16,
            uart_name="bridge")

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(
                platform.request("ddram"),
                memtype="DDR3",
                nphases=4,
                sys_clk_freq=sys_clk_freq)
            self.add_csr("ddrphy")
            sdram_module = MT41K128M16(sys_clk_freq, "1:4")
            self.register_sdram(
                self.ddrphy,
                geom_settings=sdram_module.geom_settings,
                timing_settings=sdram_module.timing_settings)

    def generate_sdram_phy_py_header(self):
        f = open("sdram_init.py", "w")
        f.write(
            get_sdram_phy_py_header(
                self.sdram.controller.settings.phy,
                self.sdram.controller.settings.timing))
        f.close()


# Load ---------------------------------------------------------------------------------------------


def load():
    prog = VivadoProgrammer()
    prog.load_bitstream("build/gateware/top.bit")


# Build --------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Minimal Arty DDR3 Design for tests with Project X-Ray")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load", action="store_true", help="Load bitstream")
    args = parser.parse_args()

    if args.load:
        load()
    soc = BaseSoC()
    builder = Builder(soc, output_dir="build", csr_csv="csr.csv")
    builder.build(run=args.build)
    soc.generate_sdram_phy_py_header()


if __name__ == "__main__":
    main()
