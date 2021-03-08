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
""" IOB bits are more complicated than can be easily expressed to segmaker.
There are couple cases that need to be handled here:

- There are some bits that are always set for IN-only ports, but are cleared
  selectively for OUT and INOUT ports.
- There are bits per each IOSTANDARD, in addition to drive patterns.  These
  can be merged to provide unique "(IOSTANDARD, DRIVE)" bit sets.
"""
import argparse


def get_name(l):
    parts = l.strip().split(' ')
    return parts[0]


def get_site(l):
    return get_name(l).split('.')[1]


def parse_bits(l):
    parts = l.strip().split(' ')
    if parts[1] in ['<0', '<const0>', '<const1>']:
        return frozenset()
    else:
        return frozenset(parts[1:])


def filter_bits(site, bits):
    """ Seperate top and bottom bits.

    Some IOSTANDARD bits are tile wide, but really only apply to a half.
    It is hard to write a fuzzer for this, but it is easy to filter by site,
    and all bits appear to have a nice hard halve seperatation in the bitidx.
    """
    if site == 'IOB_Y0':
        min_bitidx = 64
        max_bitidx = 127
    elif site == 'IOB_Y1':
        min_bitidx = 0
        max_bitidx = 63
    else:
        assert False, site

    def inner():
        for bit in bits:
            bitidx = int(bit.split('_')[1])

            if bitidx < min_bitidx or bitidx > max_bitidx:
                continue

            yield bit

    return frozenset(inner())


def process_features_sets(iostandard_lines):
    sites = {}

    for iostd_type, iostd_list in iostandard_lines.items():
        for iostd_line in iostd_list:
            feature = get_name(iostd_line)
            feature_parts = feature.split('.')
            site = get_site(iostd_line)
            iostandard = feature_parts[2]

            bits = parse_bits(iostd_line)
            bits = filter_bits(site, bits)

            key = (site, iostd_type)
            if key not in sites:
                sites[key] = {}

            group = feature_parts[3]
            if group not in sites[key]:
                sites[key][group] = {}

            if group in ['DRIVE', 'SLEW']:
                enum = feature_parts[4]
                sites[key][group][(iostandard, enum)] = bits
            elif group in ['IN', 'IN_DIFF', 'IN_ONLY', 'IN_USE', 'OUT',
                           'STEPDOWN', 'ZIBUF_LOW_PWR']:
                sites[key][group][(iostandard, None)] = bits
            else:
                assert False, group

    for site in sites:
        for iostandard, enum in sites[site]['DRIVE']:
            sites[site]['DRIVE'][(iostandard, enum)] |= sites[site]['OUT'][(
                iostandard, None)]

        for iostandard, enum in sites[site]['IN']:
            sites[site]['IN_ONLY'][(iostandard, enum)] -= sites[site]['IN'][(
                iostandard, enum)]

    common_bits = {}
    for site, iostd_type in sites:
        for group in sites[(site, iostd_type)]:
            if (site, group) not in common_bits:
                common_bits[(site, group)] = set()

            for bits in sites[(site, iostd_type)][group].values():
                common_bits[(site, group)] |= bits

    slew_in_drives = {}

    for site, iostd_type in sites:
        common_bits[(site, 'IN')] |= common_bits[(site, 'IN_DIFF')]
        common_bits[(site, 'IN_DIFF')] |= common_bits[(site, 'IN')]

        # Only DIFF IOSTANDARDS such as LVDS or TMDS do not have DRIVE,
        # STEPDOWN or SLEW features
        if iostd_type == "NORMAL":
            key = (site, iostd_type)
            common_bits[(site, 'DRIVE')] -= common_bits[(site, 'SLEW')]
            common_bits[(site, 'DRIVE')] -= common_bits[(site, 'STEPDOWN')]
            common_bits[(site, 'IN_ONLY')] |= common_bits[(site, 'DRIVE')]
            common_bits[(site, 'IN_ONLY')] -= common_bits[(site, 'STEPDOWN')]

            for iostandard, enum in sites[key]['DRIVE']:
                slew_in_drive = common_bits[
                    (site, 'SLEW')] & sites[key]['DRIVE'][(iostandard, enum)]
                if slew_in_drive:
                    if (key, iostandard) not in slew_in_drives:
                        slew_in_drives[(key, iostandard)] = set()

                    slew_in_drives[(key, iostandard)] |= slew_in_drive
                    sites[key]['DRIVE'][(iostandard, enum)] -= slew_in_drive

                sites[key]['DRIVE'][(iostandard,
                                     enum)] -= common_bits[(site, 'STEPDOWN')]

    for site, iostandard in slew_in_drives:
        for _, enum in sites[site]['SLEW']:
            sites[site]['SLEW'][(iostandard,
                                 enum)] |= slew_in_drives[(site, iostandard)]

    for site in sites:
        for iostandard, enum in sites[site]['DRIVE']:
            sites[site]['DRIVE'][(iostandard, enum)] |= sites[site]['IN_USE'][(
                iostandard, None)]

        for iostandard, enum in sites[site]['IN']:
            _, iostd_type = site
            if iostd_type == "ONLY_DIFF":
                sites[site]['IN_DIFF'][(iostandard, enum)] = \
                        sites[site]['IN'][(iostandard, enum)]
            elif sites[site]['IN_DIFF'][(iostandard, enum)]:
                sites[site]['IN_DIFF'][(iostandard, enum)] |= \
                        sites[site]['IN'][(iostandard, enum)]

    for site, iostd_type in sites:
        del sites[(site, iostd_type)]['IN_USE']
        if iostd_type == "NORMAL":
            del sites[(site, iostd_type)]['OUT']

    allow_zero = ['SLEW']

    common_groups = dict()
    for site, iostd_type in sites:
        if site not in common_groups:
            common_groups[site] = dict()

        key = (site, iostd_type)
        for group in sites[key]:
            if iostd_type == "ONLY_DIFF" and group == "IN":
                continue

            # Merge features that are identical.
            #
            # For example:
            #
            #  IOB33.IOB_Y1.LVCMOS15.IN 38_42 39_41
            #  IOB33.IOB_Y1.LVCMOS18.IN 38_42 39_41
            #
            # Must be grouped.
            for (iostandard, enum), bits in sites[key][group].items():
                if (bits, group) not in common_groups[site]:
                    common_groups[site][(bits, group)] = {
                        'IOSTANDARDS': set(),
                        'enums': set(),
                    }

                common_groups[site][(bits,
                                     group)]['IOSTANDARDS'].add(iostandard)
                if enum is not None:
                    common_groups[site][(bits, group)]['enums'].add(enum)

    visited_iostandards = list()
    for site, groups in common_groups.items():
        for (bits, group), v in groups.items():
            iostandards = v['IOSTANDARDS']
            enums = v['enums']

            # It happens that some features appear only in one of the IOB sites and not
            # in the other. This makes it hard to assign the correct features to the correct
            # site in the P&R toolchain.
            #
            # The following code makes sure that the same set of iostandards
            # (even if not really present at a site location) appears for each site
            for visited_iostandard, visited_group, visited_enums in visited_iostandards:
                same_enum = enums == visited_enums
                same_group = group == visited_group
                compatible_iostd = any(
                    x in iostandards for x in visited_iostandard)
                take_visited_iostd = len(visited_iostandard) > len(iostandards)
                if same_enum and same_group and compatible_iostd and take_visited_iostd:
                    iostandards = visited_iostandard
                    break

            visited_iostandards.append((iostandards, group, enums))

            iostandards_string = '_'.join(sorted(iostandards))

            if enums:
                feature = 'IOB33.{site}.{iostandards}.{group}.{enums}'.format(
                    site=site,
                    iostandards=iostandards_string,
                    group=group,
                    enums='_'.join(sorted(enums)),
                )
            else:
                feature = 'IOB33.{site}.{iostandards}.{group}'.format(
                    site=site,
                    iostandards=iostandards_string,
                    group=group,
                )

            if not bits and group not in allow_zero:
                continue

            neg_bits = frozenset(
                '!{}'.format(b) for b in (common_bits[(site, group)] - bits))
            print('{} {}'.format(feature, ' '.join(sorted(bits | neg_bits))))


def main():
    parser = argparse.ArgumentParser(
        description="Convert IOB rdb into good rdb."
        "")
    parser.add_argument('input_rdb')

    args = parser.parse_args()

    iostandard_lines = {
        "NORMAL": list(),
        "ONLY_DIFF": list(),
    }

    with open(args.input_rdb) as f:
        for l in f:
            if ('.SSTL' in l or '.LVCMOS' in l
                    or '.LVTTL' in l) and 'IOB_' in l:
                iostandard_lines["NORMAL"].append(l)
            elif ('.TMDS' in l or 'LVDS' in l):
                iostandard_lines["ONLY_DIFF"].append(l)
            else:
                print(l.strip())

    process_features_sets(iostandard_lines)


if __name__ == "__main__":
    main()
