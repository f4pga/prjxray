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
import glob
import os
import re
import difflib


def get_file_pairs():
    pairs_list = list()
    for path1 in glob.glob('*.bits'):
        for path2 in glob.glob('*.bits'):
            file1 = os.path.basename(path1)
            file2 = os.path.basename(path2)
            if file1 == file2:
                continue
            files_pair = [file1, file2]
            files_pair.sort()
            pairs_list.append(files_pair[0] + ":" + files_pair[1])
    pairs_set = set(pairs_list)
    for pair in pairs_set:
        file1, file2 = pair.split(":")
        yield file1, file2


def extract_parameters_string(basename):
    params_str = re.search('^design_(.*).bits$', basename)
    return params_str.group(1)


def extract_parameters(basename):
    iostandard, slew, drive = extract_parameters_string(basename).split('_')
    return iostandard, slew, drive


def generate_differing_bits(basename1, basename2):
    with open(basename1, 'r') as path1:
        with open(basename2, 'r') as path2:
            diff = difflib.unified_diff(
                path1.read().splitlines(),
                path2.read().splitlines(),
                fromfile='path1',
                tofile='path2')
            for line in diff:
                if line.startswith('---'):
                    continue
                if line.startswith('+++'):
                    continue
                if line.startswith('@'):
                    continue
                if line.startswith('-'):
                    yield extract_parameters_string(basename1), line.strip('-')
                    continue
                if line.startswith('+'):
                    yield extract_parameters_string(basename2), line.strip('+')
                    continue


class Database():
    def __init__(self, convert_bits=False):
        self.all_bits = set()
        self.properties_bits = dict()
        self.convert_bits = convert_bits
        self.populate()

    def populate(self):
        for file1, file2 in get_file_pairs():
            #print(file1 + " vs " + file2)
            for property_str, bit in generate_differing_bits(file1, file2):
                #print(property_str + " " + bit)
                self.update_all_bits(bit)
                if property_str in self.properties_bits:
                    self.properties_bits[property_str].add(bit)
                else:
                    self.properties_bits[property_str] = set()
                    self.properties_bits[property_str].add(bit)

    def update_all_bits(self, bit):
        self.all_bits.add(bit)

    def print_all_bits(self):
        print(self.all_bits)

    def get_keys(self):
        return self.properties_bits.keys()

    def print_bits(self, key):
        if key in self.properties_bits:
            print("%s: %s" % (key, self.properties_bits[key]))
        else:
            print("The specified property is not in the database")

    def convert_bit_format(self, item):
        dummy, address, word, bit = item.split("_")
        address = int(address[-2:], 16)
        bit = int(word) % 4 * 32 + int(bit)
        return "{address}_{bit}".format(address=address, bit=bit)

    def convert_header(self, header):
        converted_bits = []
        for bit in header:
            #print(bit + ":" + self.convert_bit_format(bit))
            converted_bits.append(self.convert_bit_format(bit))
        return converted_bits

    def get_csv_header(self):
        header = list(self.all_bits)
        header.sort()
        self.csv_header = header
        if self.convert_bits:
            header = self.convert_header(header)
        line = "property,v,i,r,"
        for title in header:
            line += title + ","
        return line + '\n'

    def extract_rvi_parameters(self, rvi):
        iostandard, slew, drive = rvi.split("_")
        if iostandard[-2:] == "12":
            voltage = 1.2
        elif iostandard[-2:] == "15":
            voltage = 1.5
        elif iostandard[-2:] == "18":
            voltage = 1.8
        elif iostandard[-2:] == "25":
            voltage = 2.5
        else:
            voltage = 3.3
        resistance = voltage / (int(drive) * 0.001)
        return "%.1f,%s,%.3f" % (voltage, drive, resistance)

    def get_csv_body(self):
        lines = ""
        keys = list(self.get_keys())
        keys.sort()
        for properties_key in keys:
            line = properties_key + "," + self.extract_rvi_parameters(
                properties_key) + ","
            for title in self.csv_header:
                if title in self.properties_bits[properties_key]:
                    line += "X,"
                else:
                    line += " ,"
            line += '\n'
            lines += line
        return lines

    def write_csv(self, filename):
        filename = os.getcwd() + "/" + filename
        fp = open(filename, 'w')
        fp.write(self.get_csv_header())
        fp.write(self.get_csv_body())
        fp.close()
        print("Written results to %s file.\n" % filename)


def main():
    database = Database(True)
    database.write_csv("differences.csv")


if __name__ == '__main__':
    main()
