#!/usr/bin/env python3
"""
This script allows to find missing segbits in the database.

For each tile the script loads its 'tile_type_*.json' file and looks for all
non-pseudo pips there. Next it loads corresponding 'segbits_*.db' file (if found)
and checks if those pips are listed there.

Missing segbits for pips are reported as well as missing segbit files.
"""
import logging
import json
import argparse
import os
import re

# =============================================================================


def read_pips_from_tile(tile_file):
    """
    Loads pip definition from a tile type JSON file and returns non-pseudo
    PIP name strings. Names are formatted as <dst_wire>.<src_wire>
    """

    with open(tile_file, "r") as fp:
        root = json.load(fp)
        pips = root["pips"]

        pip_names = []
        for pip in pips.values():
            if int(pip["is_pseudo"]) == 0:
                pip_names.append(
                    "{}.{}".format(pip["dst_wire"], pip["src_wire"]))

    return pip_names


def read_ppips(ppips_file):
    """
    Loads and parses ppips_*.db file. Returns a dict indexed by PIP name which
    contains their types ("always", "default" or "hint")
    """
    ppips = {}

    with open(ppips_file, "r") as fp:
        for line in fp.readlines():
            line = line.split()
            if len(line) == 2:
                full_pip_name = line[0].split(".")
                pip_name = ".".join(full_pip_name[1:])
                ppips[pip_name] = line[1]

    return ppips


def read_segbits(segbits_file):
    """
    Loads and parses segbits_*.db file. Returns only segbit names.
    """
    segbits = []

    with open(segbits_file, "r") as fp:
        for line in fp.readlines():
            line = line.split()
            if len(line) > 1:
                fields = line[0].split(".")
                segbit = ".".join(fields[1:])
                segbits.append(segbit)

    return segbits


# =============================================================================


def main():
    """
    The main
    """

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--db-root", type=str, required=True, help="Database root")
    parser.add_argument(
        "--verbose", type=int, default=0, help="Verbosity level 0-5")
    parser.add_argument(
        "--skip-tiles",
        type=str,
        nargs="*",
        default=[],
        help="Tile type name regex list for tile types to skip")
    parser.add_argument(
        "--incl-tiles",
        type=str,
        nargs="*",
        default=[],
        help="Tile type name regex list for tile types to include")

    args = parser.parse_args()

    logging.basicConfig(level=50 - args.verbose * 10, format="%(message)s")

    # List files in DB root
    files = os.listdir(args.db_root)

    # List tile types
    tile_types = []
    for file in files:
        match = re.match("^tile_type_(\w+).json$", file)
        if match:
            tile_types.append(match.group(1))

    tile_types.sort()

    # Look for missing bits
    for tile_type in tile_types:

        # Check if we should include this tile
        do_skip = len(args.incl_tiles) > 0
        for pattern in args.incl_tiles:
            if re.match(pattern, tile_type):
                do_skip = False
                break

        # Check if we should skip this tile
        for pattern in args.skip_tiles:
            if re.match(pattern, tile_type):
                do_skip = True
                break

        if do_skip:
            continue

        logging.critical(tile_type)

        # DB file names
        tile_file = os.path.join(
            args.db_root, "tile_type_{}.json".format(tile_type.upper()))
        ppips_file = os.path.join(
            args.db_root, "ppips_{}.db".format(tile_type.lower()))
        segbits_file = os.path.join(
            args.db_root, "segbits_{}.db".format(tile_type.lower()))

        # Load pips
        pips = read_pips_from_tile(tile_file)

        # Load ppips (if any)
        if os.path.isfile(ppips_file):
            ppips = read_ppips(ppips_file)
        else:
            ppips = {}

        # Load segbits (if any)
        if os.path.isfile(segbits_file):
            segbits = read_segbits(segbits_file)
        else:
            segbits = []

        # There are non-pseudo pips in this tile
        if len(pips):
            missing_bits = 0
            known_bits = 0

            # Build a list of pips to check. If a pip is listed in the ppips
            # file and it is not "default" then make it a pseudo one
            pips_to_check = []
            for pip in pips:
                if pip in ppips.keys() and ppips[pip] != "default":
                    continue
                pips_to_check.append(pip)

            # Missing segbits file
            if len(segbits) == 0:
                missing_bits = len(pips_to_check)
                logging.critical(" MISSING: no segbits file!")

            # Segbits file present
            else:

                # Check pips
                for pip in pips_to_check:
                    if pip not in segbits:

                        # A "default" pip
                        if pip in ppips.keys() and ppips[pip] == "default":
                            missing_bits += 1
                            logging.error(
                                " WARNING: no bits for pip '{}' which defaults to VCC_WIRE"
                                .format(pip))

                        # A regular pip
                        else:
                            missing_bits += 1
                            logging.error(
                                " MISSING: no bits for pip '{}'".format(pip))

                    # The pip has segbits
                    else:
                        known_bits += 1

            # Report missing bit count
            if missing_bits > 0:
                logging.critical(
                    " MISSING: no bits for {}/{} pips!".format(
                        missing_bits, missing_bits + known_bits))
            else:
                logging.critical(" OK: no missing bits")

        # No pips
        else:
            logging.warning(" OK: no pips")


# =============================================================================

if __name__ == "__main__":
    main()
