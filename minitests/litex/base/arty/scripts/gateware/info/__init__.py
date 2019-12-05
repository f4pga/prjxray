"""
Module for info embedded in the gateware / board.
"""

from litex.build.generic_platform import ConstraintError
from migen import *
from litex.soc.interconnect.csr import *

from gateware.info import git
from gateware.info import dna
from gateware.info import xadc
from gateware.info import platform as platform_info


class Info(Module, AutoCSR):
    def __init__(self, platform, target_name):
        self.submodules.dna = dna.DNA()
        self.submodules.git = git.GitInfo()
        target = target_name.lower()[:-3]
        self.submodules.platform = platform_info.PlatformInfo(
            platform.name, target)

        if "xc7" in platform.device:
            self.submodules.xadc = xadc.XADC()
