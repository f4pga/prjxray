#!/usr/bin/env python3

from __future__ import print_function

import fasm
import argparse
import json
import os
import os.path
import csv

from collections import defaultdict

from prjxray import fasm_assembler
from prjxray.db import Database
from prjxray.roi import Roi


class FASMSyntaxError(SyntaxError):
    pass


def dump_frames_verbose(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]
        print(
            '0x%08X ' % addr + ', '.join(['0x%08X' % w for w in words]) +
            '...')


def dump_frames_sparse(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]

        # Skip frames without filled words
        for w in words:
            if w:
                break
        else:
            continue

        print('Frame @ 0x%08X' % addr)
        for i, w in enumerate(words):
            if w:
                print('  % 3d: 0x%08X' % (i, w))


def dump_frm(f, frames):
    '''Write a .frm file given a list of frames, each containing a list of 101 32 bit words'''
    for addr in sorted(frames.keys()):
        words = frames[addr]
        f.write(
            '0x%08X ' % addr + ','.join(['0x%08X' % w for w in words]) + '\n')


def find_pudc_b(db):
    """ Find PUDC_B pin func in grid, and return the tile and site prefix.

    The PUDC_B pin is a special 7-series pin that controls unused pin pullup.

    If the PUDC_B is unused, it is configured as an input with a PULLUP.

    """
    grid = db.grid()

    pudc_b_tile_site = None
    for tile in grid.tiles():
        gridinfo = grid.gridinfo_at_tilename(tile)

        for site, pin_function in gridinfo.pin_functions.items():
            if 'PUDC_B' in pin_function:
                assert pudc_b_tile_site == None, (
                    pudc_b_tile_site, (tile, site))
                iob_y = int(site[-1]) % 2

                pudc_b_tile_site = (tile, 'IOB_Y{}'.format(iob_y))

    return pudc_b_tile_site


def get_iob_sites(db, tile_name):
    """
    Yields prjxray site names for given IOB tile name
    """
    grid = db.grid()
    gridinfo = grid.gridinfo_at_tilename(tile_name)

    for site in gridinfo.sites:
        site_y = int(site[-1]) % 2
        yield "IOB_Y{}".format(site_y)


def run(
        db_root,
        part,
        filename_in,
        f_out,
        sparse=False,
        roi=None,
        debug=False,
        emit_pudc_b_pullup=False):
    db = Database(db_root)
    assembler = fasm_assembler.FasmAssembler(db)

    set_features = set()

    def feature_callback(feature):
        set_features.add(feature)

    assembler.set_feature_callback(feature_callback)

    # Build mapping of tile to IO bank
    tile_to_bank = {}
    bank_to_tile = defaultdict(lambda: set())

    if part is not None:
        with open(os.path.join(db_root, part + "_package_pins.csv"),
                  "r") as fp:
            reader = csv.DictReader(fp)
            package_pins = [l for l in reader]

        for pin in package_pins:
            bank_to_tile[pin["bank"]].add(pin["tile"])
            tile_to_bank[pin["tile"]] = pin["bank"]

    if emit_pudc_b_pullup:
        pudc_b_in_use = False
        pudc_b_tile_site = find_pudc_b(db)

        def check_for_pudc_b(set_feature):
            feature_callback(set_feature)
            parts = set_feature.feature.split('.')

            if parts[0] == pudc_b_tile_site[0] and parts[
                    1] == pudc_b_tile_site[1]:
                nonlocal pudc_b_in_use
                pudc_b_in_use = True

        if pudc_b_tile_site is not None:
            assembler.set_feature_callback(check_for_pudc_b)

    extra_features = []
    if roi:
        with open(roi) as f:
            roi_j = json.load(f)
        x1 = roi_j['info']['GRID_X_MIN']
        x2 = roi_j['info']['GRID_X_MAX']
        y1 = roi_j['info']['GRID_Y_MIN']
        y2 = roi_j['info']['GRID_Y_MAX']

        assembler.mark_roi_frames(Roi(db=db, x1=x1, x2=x2, y1=y1, y2=y2))

        if 'required_features' in roi_j:
            extra_features = list(
                fasm.parse_fasm_string('\n'.join(roi_j['required_features'])))

    # Get required extra features for the part
    required_features = db.get_required_fasm_features(part)
    extra_features += list(
        fasm.parse_fasm_string('\n'.join(required_features)))

    assembler.parse_fasm_filename(filename_in, extra_features=extra_features)

    if emit_pudc_b_pullup and not pudc_b_in_use and pudc_b_tile_site is not None:
        # Enable IN-only and PULLUP on PUDC_B IOB.
        #
        # TODO: The following FASM string only works on Artix 50T and Zynq 10
        # fabrics.  It is known to be wrong for the K70T fabric, but it is
        # unclear how to know which IOSTANDARD to use.
        missing_features = []
        for line in fasm.parse_fasm_string("""
{tile}.{site}.LVCMOS12_LVCMOS15_LVCMOS18_LVCMOS25_LVCMOS33_LVTTL_SSTL135.IN_ONLY
{tile}.{site}.LVCMOS25_LVCMOS33_LVTTL.IN
{tile}.{site}.PULLTYPE.PULLUP
""".format(
                tile=pudc_b_tile_site[0],
                site=pudc_b_tile_site[1],
        )):
            assembler.add_fasm_line(line, missing_features)

        if missing_features:
            raise fasm_assembler.FasmLookupError('\n'.join(missing_features))

    if part is not None:
        # Make a set of all used IOB tiles and sites. Look for the "STEPDOWN"
        # feature. If one is set for an IOB then set it for all other IOBs of
        # the same bank.
        stepdown_tags = set()
        stepdown_banks = set()
        used_iob_sites = set()

        for set_feature in set_features:
            feature = set_feature.feature
            parts = feature.split(".")
            if len(parts) >= 3:
                tile, site, tag = feature.split(".", maxsplit=2)
                if "IOB33" in tile:
                    used_iob_sites.add((
                        tile,
                        site,
                    ))
                if "STEPDOWN" in tag:
                    stepdown_banks.add(tile_to_bank[tile])
                    stepdown_tags.add(tag)

        # Set the feature for unused IOBs
        missing_features = []

        for bank in stepdown_banks:
            for tile in bank_to_tile[bank]:
                for site in get_iob_sites(db, tile):

                    if (tile, site) in used_iob_sites:
                        continue

                    for tag in stepdown_tags:
                        feature = "{}.{}.{}".format(tile, site, tag)
                        for line in fasm.parse_fasm_string(feature):
                            assembler.add_fasm_line(line, missing_features)

        if missing_features:
            raise fasm_assembler.FasmLookupError('\n'.join(missing_features))

    frames = assembler.get_frames(sparse=sparse)

    if debug:
        dump_frames_sparse(frames)

    dump_frm(f_out, frames)


def main():
    parser = argparse.ArgumentParser(
        description=
        'Convert FPGA configuration description ("FPGA assembly") into binary frame equivalent'
    )

    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    db_part = os.getenv("XRAY_PART")
    db_part_kwargs = {}
    if db_part is None:
        db_part_kwargs['required'] = True
    else:
        db_part_kwargs['required'] = False
        db_part_kwargs['default'] = db_part

    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)
    parser.add_argument(
        '--part',
        help="Part name. When not given defaults to XRAY_PART env. var.",
        **db_part_kwargs)
    parser.add_argument(
        '--sparse', action='store_true', help="Don't zero fill all frames")
    parser.add_argument(
        '--roi',
        help="ROI design.json file defining which tiles are within the ROI.")
    parser.add_argument(
        '--emit_pudc_b_pullup',
        help="Emit an IBUF and PULLUP on the PUDC_B pin if unused",
        action='store_true')
    parser.add_argument(
        '--debug', action='store_true', help="Print debug dump")
    parser.add_argument('fn_in', help='Input FPGA assembly (.fasm) file')
    parser.add_argument(
        'fn_out',
        default='/dev/stdout',
        nargs='?',
        help='Output FPGA frame (.frm) file')

    args = parser.parse_args()
    run(
        db_root=args.db_root,
        part=args.part,
        filename_in=args.fn_in,
        f_out=open(args.fn_out, 'w'),
        sparse=args.sparse,
        roi=args.roi,
        debug=args.debug,
        emit_pudc_b_pullup=args.emit_pudc_b_pullup)


if __name__ == '__main__':
    main()
