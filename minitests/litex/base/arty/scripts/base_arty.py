#!/usr/bin/env python3

import argparse

import arty
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.integration.soc_core import mem_decoder
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from liteeth.core.mac import LiteEthMAC
from liteeth.phy import LiteEthPHY

from utils import csr_map_update
from base import SoC as BaseSoC


class LinuxSoC(BaseSoC):
    csr_peripherals = (
        "ethphy",
        "ethmac",
    )
    csr_map_update(BaseSoC.csr_map, csr_peripherals)

    mem_map = {
        "ethmac": 0x30000000,  # (shadow @0xb0000000)
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, *args, **kwargs):
        platform = arty.Platform()
        kwargs['cpu_variant'] = "linux"

        BaseSoC.__init__(self, platform, *args, **kwargs)

        self.submodules.ethphy = LiteEthPHY(
            platform.request("eth_clocks"), platform.request("eth"))
        self.submodules.ethmac = LiteEthMAC(
            phy=self.ethphy,
            dw=32,
            interface="wishbone",
            endianness=self.cpu.endianness)
        self.add_wb_slave(mem_decoder(self.mem_map["ethmac"]), self.ethmac.bus)
        self.add_memory_region(
            "ethmac", self.mem_map["ethmac"] | self.shadow_base, 0x2000)

        self.ethphy.crg.cd_eth_rx.clk.attr.add("keep")
        self.ethphy.crg.cd_eth_tx.clk.attr.add("keep")
        #self.platform.add_period_constraint(self.crg.cd_sys.clk, 10.0)
        self.platform.add_period_constraint(
            self.ethphy.crg.cd_eth_rx.clk, 40.0)
        self.platform.add_period_constraint(
            self.ethphy.crg.cd_eth_tx.clk, 40.0)
        self.platform.add_false_path_constraints(
            self.crg.cd_sys.clk, self.ethphy.crg.cd_eth_rx.clk,
            self.ethphy.crg.cd_eth_tx.clk)

        self.add_interrupt("ethmac")

    def configure_iprange(self, iprange):
        iprange = [int(x) for x in iprange.split(".")]
        while len(iprange) < 4:
            iprange.append(0)
        # Our IP address
        self._configure_ip("LOCALIP", iprange[:-1] + [50])
        # IP address of tftp host
        self._configure_ip("REMOTEIP", iprange[:-1] + [100])

    def _configure_ip(self, ip_type, ip):
        for i, e in enumerate(ip):
            s = ip_type + str(i + 1)
            s = s.upper()
            self.add_constant(s, e)


# Build --------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Arty")
    builder_args(parser)
    soc_sdram_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    cls = LinuxSoC
    soc = cls(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args))


if __name__ == "__main__":
    main()
