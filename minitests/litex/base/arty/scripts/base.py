# Support for the Digilent Arty Board
from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.integration.soc_core import mem_decoder
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.interconnect import wishbone
from litex.soc.cores.clock import S7PLL, S7IDELAYCTRL

from litedram.modules import MT41K128M16
from litedram.phy import a7ddrphy
from litedram.core import ControllerSettings

from gateware import cas
from gateware import spi_flash

from utils import csr_map_update, period_ns


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys4x = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200 = ClockDomain()
        self.clock_domains.cd_eth = ClockDomain()

        # # #
        pll_clkin = Signal()
        self.specials += Instance(
            "BUFG", i_I=platform.request("clk100"), o_O=pll_clkin)
        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset"))
        pll.register_clkin(pll_clkin, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys4x, 4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200, 200e6)
        pll.create_clkout(self.cd_eth, 25e6)
        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)
        # 25MHz clock for Ethernet
        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)


class BaseSoC(SoCSDRAM):
    csr_peripherals = (
        "spiflash",
        "ddrphy",
        "info",
        "cas",
    )
    csr_map_update(SoCSDRAM.csr_map, csr_peripherals)

    SoCSDRAM.mem_map = {
        "rom": 0x00000000,
        "sram": 0x10000000,
        "main_ram": 0x40000000,
        "csr": 0xe0000000,
    }

    mem_map = {
        "spiflash": 0x20000000,
        "emulator_ram": 0x50000000,
    }
    mem_map.update(SoCSDRAM.mem_map)

    def __init__(self, platform, spiflash="spiflash_1x", **kwargs):
        if 'integrated_rom_size' not in kwargs:
            kwargs['integrated_rom_size'] = 0x8000
        if 'integrated_sram_size' not in kwargs:
            kwargs['integrated_sram_size'] = 0x8000
        kwargs['uart_baudrate'] = 921600

        clk_freq = int(100e6)
        SoCSDRAM.__init__(self, platform, clk_freq, **kwargs)

        self.submodules.crg = _CRG(platform, clk_freq)
        self.crg.cd_sys.clk.attr.add("keep")
        self.platform.add_period_constraint(
            self.crg.cd_sys.clk, period_ns(clk_freq))

        # Basic peripherals
        #self.submodules.info = info.Info(platform, self.__class__.__name__)
        self.submodules.cas = cas.ControlAndStatus(platform, clk_freq)
        # spi flash
        spiflash_pads = platform.request(spiflash)
        spiflash_pads.clk = Signal()
        spiflash_dummy = {
            "spiflash_1x": 9,
            "spiflash_4x": 11,
        }
        self.submodules.spiflash = spi_flash.SpiFlash(
            spiflash_pads,
            dummy=spiflash_dummy[spiflash],
            div=platform.spiflash_clock_div,
            endianness=self.cpu.endianness)
        self.add_constant("SPIFLASH_PAGE_SIZE", 256)
        self.add_constant("SPIFLASH_SECTOR_SIZE", 0x10000)
        self.add_wb_slave(
            mem_decoder(self.mem_map["spiflash"]), self.spiflash.bus)
        self.add_memory_region(
            "spiflash", self.mem_map["spiflash"], 16 * 1024 * 1024)

        if self.cpu_type == "vexriscv" and self.cpu_variant == "linux":
            size = 0x4000
            self.submodules.emulator_ram = wishbone.SRAM(size)
            self.register_mem(
                "emulator_ram", self.mem_map["emulator_ram"],
                self.emulator_ram.bus, size)

        bios_size = 0x8000
        self.flash_boot_address = self.mem_map[
            "spiflash"] + platform.gateware_size + bios_size
        self.add_constant("FLASH_BOOT_ADDRESS", self.flash_boot_address)

        # sdram
        sdram_module = MT41K128M16(self.clk_freq, "1:4")
        self.submodules.ddrphy = a7ddrphy.A7DDRPHY(platform.request("ddram"))
        self.add_constant("READ_LEVELING_BITSLIP", 3)
        self.add_constant("READ_LEVELING_DELAY", 14)
        controller_settings = ControllerSettings(
            with_bandwidth=True, cmd_buffer_depth=8, with_refresh=True)
        self.register_sdram(
            self.ddrphy,
            sdram_module.geom_settings,
            sdram_module.timing_settings,
            controller_settings=controller_settings)


SoC = BaseSoC
