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
"""
This script performs the analysis of disassembled bitstream and design information.
It correlates presence/absence of particular fasm features in the bitstream
with presence/absence of a particular IOB type. It also checks for features
that are set for unused IOBs that are in the same bank as the used ones.

The list of available fasm features is read from the prjxray database. The
analysis result is written to a CSV file.
"""
import os
import argparse
import json
import random

from collections import defaultdict

from prjxray import util
import fasm

# =============================================================================


def load_iob_segbits():
    """
    Loads IOB segbits from the database to get fasm feature list.
    This function assumes:
    - LIOB33/RIOB33 have the same features.
    - IOB_Y0 and IOB_Y1 have the same features (at least those of interest).
    """
    features = []

    fname = os.path.join(util.get_db_root(), "segbits_liob33.db")
    with open(fname, "r") as fp:
        for line in fp:

            line = line.strip()
            if len(line) == 0:
                continue

            # Parse the line
            fields = line.split(maxsplit=1)
            feature = fields[0]
            bits = fields[1]

            # Parse the feature
            parts = feature.split(".", maxsplit=3)
            if len(parts) >= 3 and parts[1] == "IOB_Y0":
                features.append(".".join(parts[2:]))

    return features


def correlate_features(features, tile, site, set_features):
    """
    Correlate each feature with the fasm disassembly for given tile/site.

    Given a set of all possible fasm features (for an IOB) in the first
    argument, checks whether they are set or cleared for the given tile+site in
    a design. The parameter set_features contains fasm dissassembly of the
    design.

    Returns a list of tuples with feature names and whether they are set or not.
    """
    result = []

    for feature in features:
        full_feature = "{}.{}.{}".format(tile, site, feature)
        if full_feature in set_features:
            result.append((
                feature,
                True,
            ))
        else:
            result.append((
                feature,
                False,
            ))

    return result


def run():
    """
    Main.
    """

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--design", type=str, required=True, help="Design JSON file")
    parser.add_argument(
        "--fasm", type=str, required=True, help="Decoded fasm file")
    parser.add_argument(
        "-o", type=str, default="results.csv", help="Output CSV file")
    parser.add_argument("-j", type=str, default=None, help="Output JSON file")

    args = parser.parse_args()

    # Load IOB features
    features = load_iob_segbits()

    # Load the design data
    with open(args.design, "r") as fp:
        design = json.load(fp)

    # Load disassembled fasm
    fasm_tuples = fasm.parse_fasm_filename(args.fasm)
    set_features = fasm.fasm_tuple_to_string(fasm_tuples).split("\n")

    # Correlate features for given IOB types
    results = []
    for region in design:
        result = dict(region["iosettings"])

        for l in ["input", "output", "inout", "unused_sites"]:

            # TODO: Check if this is true eg. for all unused sites, not just
            # one random site.
            tile, site = random.choice(region[l]).split(".")
            matches = correlate_features(features, tile, site, set_features)

            result[l] = matches

        results.append(result)

    # Save results
    if args.j:
        with open(args.j, "w") as fp:
            json.dump(results, fp, indent=2, sort_keys=True)

    # Save results to CSV
    with open(args.o, "w") as fp:
        csv_data = defaultdict(lambda: {})

        # Collect data
        for result in results:
            iostandard = result["iostandard"]
            drive = result["drive"]
            slew = result["slew"]

            if drive is None:
                drive = "_FIXED"

            iosettings = "{}.I{}.{}".format(iostandard, drive, slew)

            is_diff = "DIFF" in iostandard

            for feature in sorted(features):
                I = [f[1] for f in result["input"] if f[0] == feature and f[1]]
                O = [
                    f[1] for f in result["output"] if f[0] == feature and f[1]
                ]
                T = [f[1] for f in result["inout"] if f[0] == feature and f[1]]
                U = [
                    f[1]
                    for f in result["unused_sites"]
                    if f[0] == feature and f[1]
                ]

                s = "".join(
                    [
                        "I" if len(I) > 0 else "",
                        "O" if len(O) > 0 else "",
                        "T" if len(T) > 0 else "",
                        "U" if len(U) > 0 else "",
                    ])

                csv_data[iosettings][feature] = s

        # Write header
        line = ["iosettings"] + sorted(features)
        fp.write(",".join(line) + "\n")

        # Write data
        for iosettings in sorted(csv_data.keys()):
            data = csv_data[iosettings]
            line = [iosettings
                    ] + [data[feature] for feature in sorted(features)]

            fp.write(",".join(line) + "\n")


if __name__ == "__main__":
    run()
