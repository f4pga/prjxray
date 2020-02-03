#!/usr/bin/env python3

import sys
import time

from litex import RemoteClient

from sdram_init import *

wb = RemoteClient(debug=False)
wb.open()

# # #

# get identifier
fpga_id = ""
for i in range(256):
    c = chr(wb.read(wb.bases.identifier_mem + 4*i) & 0xff)
    fpga_id += c
    if c == "\0":
        break
print(fpga_id)

# software control
wb.regs.sdram_dfii_control.write(0)

# sdram initialization
for i, (comment, a, ba, cmd, delay) in enumerate(init_sequence):
    print(comment)
    wb.regs.sdram_dfii_pi0_address.write(a)
    wb.regs.sdram_dfii_pi0_baddress.write(ba)
    if i < 2:
        wb.regs.sdram_dfii_control.write(cmd)
    else:
        wb.regs.sdram_dfii_pi0_command.write(cmd)
        wb.regs.sdram_dfii_pi0_command_issue.write(1)

# hardware control
wb.regs.sdram_dfii_control.write(dfii_control_sel)

def seed_to_data(seed, random=True):
    if random:
        return (1664525*seed + 1013904223) & 0xffffffff
    else:
        return seed

def write_pattern(length):
    for i in range(length):
        wb.write(wb.mems.main_ram.base + 4*i, seed_to_data(i))

def check_pattern(length, debug=False):
    errors = 0
    for i in range(length):
        error = 0
        if wb.read(wb.mems.main_ram.base + 4*i) != seed_to_data(i):
            error = 1
            if debug:
                print("{}: 0x{:08x}, 0x{:08x} KO".format(i, wb.read(wb.mems.main_ram.base + 4*i), seed_to_data(i)))
        else:
            if debug:
                print("{}: 0x{:08x}, 0x{:08x} OK".format(i, wb.read(wb.mems.main_ram.base + 4*i), seed_to_data(i)))
        errors += error
    return errors

# find working bitslips and delays
nbitslips = 8
ndelays   = 32
nmodules  = 2
nwords    = 16

for bitslip in range(nbitslips):
    print("bitslip {:d}: |".format(bitslip), end="")
    for delay in range(ndelays):
        for module in range(nmodules):
            wb.regs.ddrphy_dly_sel.write(1<<module)
            wb.regs.ddrphy_rdly_dq_rst.write(1)
            wb.regs.ddrphy_rdly_dq_bitslip_rst.write(1)
            for i in range(bitslip):
                wb.regs.ddrphy_rdly_dq_bitslip.write(1)
            for i in range(delay):
                wb.regs.ddrphy_rdly_dq_inc.write(1)
        write_pattern(nwords)
        errors = check_pattern(nwords)
        if errors:
            print("..|", end="")
        else:
            print("{:02d}|".format(delay), end="")
        sys.stdout.flush()
    print("")

# # #

wb.close()
