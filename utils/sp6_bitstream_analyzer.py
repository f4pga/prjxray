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
'''
Spartan 6 bitstream analyzer tool.

This script reads a Spartan6 bitstream and prints out some useful information.
It can also create a frames file with the configuration data words.
The bitstream is analyzed word by word and interpreted according to
the UG380 Configuration User Guide.

The tool can be used to derive the initialization, startup and finalization
sequence as well as the configuration data. The latter is written to a frames
file which can be used by the bitstream tools such as frames2bit to generate
a valid bitstream.
'''

import argparse
from io import StringIO

from prjxray.util import OpenSafeFile

conf_regs = {
    0: "CRC",
    1: "FAR_MAJ",
    2: "FAR_MIN",
    3: "FDRI",
    4: "FDRO",
    5: "CMD",
    6: "CTL",
    7: "MASK",
    8: "STAT",
    9: "LOUT",
    10: "COR1",
    11: "COR2",
    12: "PWRDN_REG",
    13: "FLR",
    14: "IDCODE",
    15: "CWDT",
    16: "HC_OPT_REG",
    18: "CSBO",
    19: "GENERAL1",
    20: "GENERAL2",
    21: "GENERAL3",
    22: "GENERAL4",
    23: "GENERAL5",
    24: "MODE_REG",
    25: "PU_GWE",
    26: "PU_GTS",
    27: "MFWR",
    28: "CCLK_FREQ",
    29: "SEU_OPT",
    30: "EXP_SIGN",
    31: "RDBK_SIGN",
    32: "BOOTSTS",
    33: "EYE_MASK",
    34: "CBC_REG"
}

cmd_reg_codes = {
    0: "NULL",
    1: "WCFG",
    2: "MFW",
    3: "LFRM",
    4: "RCFG",
    5: "START",
    7: "RCRC",
    8: "AGHIGH",
    10: "GRESTORE",
    11: "SHUTDOWN",
    13: "DESYNC",
    14: "IPROG"
}

opcodes = ("NOP", "READ", "WRITE", "UNKNOWN")


def KnuthMorrisPratt(text, pattern):
    '''
    Yields all starting positions of copies of the pattern in the text.
    Calling conventions are similar to string.find, but its arguments can be
    lists or iterators, not just strings, it returns all matches, not just
    the first one, and it does not need the whole text in memory at once.
    Whenever it yields, it will have read the text exactly up to and including
    the match that caused the yield.
    '''

    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos - shift]:
            shift += shifts[pos - shift]
        shifts[pos + 1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            yield startPos


class Bitstream:
    def __init__(self, file_name, verbose=False):
        self.frame_data = []
        self.idcode = 0
        self.exp_sign = 0
        self.far_min = 0
        self.far_maj = 0
        self.curr_fdri_write_len = 0
        self.curr_crc_check = 0
        self.fdri_in_progress = False
        with OpenSafeFile(file_name, "rb") as f:
            self.bytes = f.read()
        pos, self.header = self.get_header()
        self.body = [
            (i << 8) | j
            for i, j in zip(self.bytes[pos::2], self.bytes[pos + 1::2])
        ]
        self.parse_bitstream(verbose)

    def get_header(self):
        pos = next(KnuthMorrisPratt(self.bytes, [0xaa, 0x99, 0x55, 0x66]))
        return pos + 4, self.bytes[:pos + 4]

    def parse_bitstream(self, verbose):
        payload_len = 0
        for word in self.body:
            if payload_len > 0:
                if verbose:
                    print("\tWord: ", hex(word))
                payload_len = self.parse_reg(
                    reg_addr, word, payload_len, verbose)
                continue
            else:
                packet_header = self.parse_packet_header(word)
                opcode = packet_header["opcode"]
                reg_addr = packet_header["reg_addr"]
                words = packet_header["word_count"]
                type = packet_header["type"]
                if verbose:
                    print(
                        "\tWord: ", hex(word),
                        'Type: {}, Op: {}, Addr: {}, Words: {}'.format(
                            type, opcodes[opcode], reg_addr, words))
                if opcode and reg_addr in conf_regs:
                    payload_len = words
                    continue

    def parse_packet_header(self, word):
        type = (word >> 13) & 0x7
        opcode = (word >> 11) & 0x3
        reg_addr = (word >> 5) & 0x3F
        if type == 1:
            word_count = word & 0x1F
        elif type == 2:
            word_count = 2
        else:
            word_count = 0
        return {
            "type": type,
            "opcode": opcode,
            "reg_addr": reg_addr,
            "word_count": word_count
        }

    def parse_command(self, word):
        return cmd_reg_codes[word]

    def parse_cor1(self, word):
        return word

    def parse_cor2(self, word):
        return word

    def parse_ctl(self, word):
        #decryption
        dec = (word >> 6) & 1
        #security bits
        sb = (word >> 4) & 3
        #persist
        p = (word >> 3) & 1
        #use efuse
        efuse = (word >> 2) & 1
        #crc extstat disable
        crc = (word >> 1) & 1
        return {
            "decryption": dec,
            "security bits": sb,
            "pesist": p,
            "use efuse": efuse,
            "crc extstat disable": crc
        }

    def parse_cclk_freq(self, word):
        ext_mclk = (word >> 14) & 1
        mclk_freq = word & 0x3FF
        return (ext_mclk, mclk_freq)

    def parse_pwrdn(self, word):
        en_eyes = (word >> 14) & 1
        filter_b = (word >> 5) & 1
        en_pgsr = (word >> 4) & 1
        en_pwrdn = (word >> 2) & 1
        keep_sclk = word & 1
        return {
            "en_eyes": en_eyes,
            "filter_b": filter_b,
            "en_pgsr": en_pgsr,
            "en_pwrdn": en_pwrdn,
            "keep_sclk": keep_sclk
        }

    def parse_eye_mask(self, word):
        return word & 0xFF

    def parse_hc_opt(self, word):
        return (word >> 6) & 1

    def parse_cwdt(self, word):
        return word

    def parse_pu_gwe(self, word):
        return word & 0x3FF

    def parse_pu_gts(self, word):
        return word & 0x3FF

    def parse_mode(self, word):
        new_mode = (word >> 13) & 0x1
        buswidth = (word >> 11) & 0x3
        bootmode = (word >> 8) & 0x7
        bootvsel = word & 0xFF
        return {
            "new_mode": new_mode,
            "buswidth": buswidth,
            "bootmode": bootmode,
            "bootvsel": bootvsel
        }

    def parse_seu(self, word):
        seu_freq = (word >> 4) & 0x3FF
        seu_run_on_err = (word >> 3) & 0x1
        glut_mask = (word >> 1) & 0x1
        seu_enable = word & 0x1
        return {
            "seu_freq": seu_freq,
            "seu_run_on_err": seu_run_on_err,
            "glut_mask": glut_mask,
            "seu_enable": seu_enable
        }

    def parse_reg(self, reg_addr, word, payload_len, verbose):
        reg = conf_regs[reg_addr]
        if reg == "CMD":
            command = self.parse_command(word)
            if verbose:
                print("Command: {}\n".format(command))
        elif reg == "FLR":
            frame_length = word
            if verbose:
                print("Frame length: {}\n".format(frame_length))
        elif reg == "COR1":
            conf_options = self.parse_cor1(word)
            if verbose:
                print("COR1 options: {}\n".format(conf_options))
        elif reg == "COR2":
            conf_options = self.parse_cor2(word)
            if verbose:
                print("COR2 options: {}\n".format(conf_options))
        elif reg == "IDCODE":
            assert payload_len < 3
            if payload_len == 2:
                self.idcode = word << 16
            elif payload_len == 1:
                self.idcode |= word
                if verbose:
                    print("IDCODE: {}\n".format(hex(self.idcode)))
        elif reg == "MASK":
            mask = word
            if verbose:
                print("Mask value: {}\n".format(mask))
        elif reg == "CTL":
            ctl_options = self.parse_ctl(word)
            if verbose:
                print("CTL options: {}\n".format(ctl_options))
        elif reg == "CCLK_FREQ":
            cclk_freq_options = self.parse_cclk_freq(word)
            if verbose:
                print("CCLK_FREQ options: {}\n".format(cclk_freq_options))
        elif reg == "PWRDN_REG":
            suspend_reg_options = self.parse_pwrdn(word)
            if verbose:
                print("{} options: {}\n".format(reg, suspend_reg_options))
        elif reg == "EYE_MASK":
            eye_mask = self.parse_eye_mask(word)
            if verbose:
                print("{} options: {}\n".format(reg, eye_mask))
        elif reg == "HC_OPT_REG":
            hc_options = self.parse_hc_opt(word)
            if verbose:
                print("{} options: {}\n".format(reg, hc_options))
        elif reg == "CWDT":
            cwdt_options = self.parse_cwdt(word)
            if verbose:
                print("{} options: {}\n".format(reg, cwdt_options))
        elif reg == "PU_GWE":
            pu_gwe_sequence = self.parse_pu_gwe(word)
            if verbose:
                print("{} options: {}\n".format(reg, pu_gwe_sequence))
        elif reg == "PU_GTS":
            pu_gts_sequence = self.parse_pu_gts(word)
            if verbose:
                print("{} options: {}\n".format(reg, pu_gts_sequence))
        elif reg == "MODE_REG":
            mode_options = self.parse_mode(word)
            if verbose:
                print("{} options: {}\n".format(reg, mode_options))
        elif reg == "GENERAL1" or reg == "GENERAL2" \
             or reg == "GENERAL3" or reg == "GENERAL4" \
             or reg == "GENERAL5":
            general_options = word
            if verbose:
                print("{} options: {}\n".format(reg, general_options))
        elif reg == "SEU_OPT":
            seu_options = self.parse_seu(word)
            if verbose:
                print("{} options: {}\n".format(reg, seu_options))
        elif reg == "EXP_SIGN":
            if payload_len == 2:
                self.exp_sign = word << 16
            elif payload_len == 1:
                self.exp_sign |= word
                if verbose:
                    print("{}: {}\n".format(reg, self.exp_sign))
        elif reg == "FAR_MAJ":
            if payload_len == 2:
                self.current_far_maj = word
            elif payload_len == 1:
                self.current_far_min = word
                if verbose:
                    print(
                        "{}: {} FAR_MIN: {}\n".format(
                            reg, self.far_maj, self.far_min))
        elif reg == "FDRI":
            if self.fdri_in_progress:
                self.frame_data.append(word)
                if payload_len == 1:
                    self.fdri_in_progress = False
                    return 0
            elif payload_len == 2:
                self.curr_fdri_write_len = (word & 0xFFF) << 16
            elif payload_len == 1:
                self.curr_fdri_write_len |= word
                self.fdri_in_progress = True
                # Check if 0 words actually means read something
                payload_len = self.curr_fdri_write_len + 2
                if verbose:
                    print("{}: {}\n".format(reg, self.curr_fdri_write_len))
                return payload_len
        elif reg == "CRC":
            if payload_len == 2:
                self.curr_crc_check = (word & 0xFFF) << 16
            elif payload_len == 1:
                self.curr_crc_check |= word
                if verbose:
                    print("{}: {}\n".format(reg, self.curr_crc_check))
        payload_len -= 1
        return payload_len

    def write_frames_txt(self, file_name):
        '''Write frame data in a more readable format'''
        frame_stream = StringIO()
        for i in range(len(self.frame_data)):
            if i % 65 == 0:
                frame_stream.write("\nFrame {:4}\n".format(i // 65))
            #IOB word
            if i % 65 == 32:
                frame_stream.write(
                    "\n#{:3}:{:6}\n".format(i % 65, hex(self.frame_data[i])))
            else:
                frame_stream.write(
                    "#{:3}:{:6},".format(i % 65, hex(self.frame_data[i])))
        with OpenSafeFile(file_name, "w") as f:
            print(frame_stream.getvalue(), file=f)

    def write_frames(self, file_name):
        '''Write configuration data to frames file'''
        frame_stream = StringIO()
        for i in range(len(self.frame_data)):
            if i % 65 == 0:
                frame_stream.write("0x{:08x} ".format(i // 65))
            frame_stream.write("0x{:04x}".format(self.frame_data[i]))
            if i % 65 == 64:
                frame_stream.write("\n")
            elif i < len(self.frame_data) - 1:
                frame_stream.write(",")
        with OpenSafeFile(file_name, "w") as f:
            print(frame_stream.getvalue(), file=f)


def main(args):
    verbose = not args.silent
    bitstream = Bitstream(args.bitstream, verbose)
    print("Frame data length: ", len(bitstream.frame_data))
    if args.frames_out:
        bitstream.write_frames(args.frames_out)
        if verbose:
            bitstream.write_frames_txt(args.frames_out + ".txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--bitstream', help='Input bitstream')
    parser.add_argument('--frames_out', help='Output frames file')
    parser.add_argument(
        '--silent', help="Don't print analysis details", action='store_true')
    args = parser.parse_args()
    main(args)
