#!/usr/bin/env python3

from __future__ import print_function

import fasm
import argparse
import json
import os
import os.path

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


def run(
        db_root,
        filename_in,
        f_out,
        sparse=False,
        roi=None,
        debug=False,
        emit_pudc_b_pullup=False):
    db = Database(db_root)
    assembler = fasm_assembler.FasmAssembler(db)

    if emit_pudc_b_pullup:
        pudc_b_in_use = False
        pudc_b_tile_site = find_pudc_b(db)

        def check_for_pudc_b(set_feature):
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
            extra_features = fasm.parse_fasm_string(
                '\n'.join(roi_j['required_features']))

    # Get required features for the part
    # TODO: Specify the part explicitly ?
    required_features = db.get_required_fasm_features(None)
    extra_features += fasm.parse_fasm_string('\n'.join(required_features))

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

    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)
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
        filename_in=args.fn_in,
        f_out=open(args.fn_out, 'w'),
        sparse=args.sparse,
        roi=args.roi,
        debug=args.debug,
        emit_pudc_b_pullup=args.emit_pudc_b_pullup)


if __name__ == '__main__':
    main()
