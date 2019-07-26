#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker
from prjxray import verilog
import os
import json


def bitfilter(frame, word):
    if frame < 38:
        return False

    return True


def mk_drive_opt(iostandard, drive):
    if drive is None:
        drive = '_FIXED'
    return '{}.DRIVE.I{}'.format(iostandard, drive)


def skip_broken_tiles(d):
    """ Skip tiles that appear to have bits always set.

    This is likely caused by a defect?

    """
    if os.getenv('XRAY_DATABASE') == 'artix7' and d['tile'] == 'LIOB33_X0Y43':
        return True
    if os.getenv('XRAY_DATABASE') == 'zynq7' and d['tile'] == 'RIOB33_X31Y43':
        return True

    return False


def drives_for_iostandard(iostandard):
    if iostandard in ['LVTTL', 'LVCMOS18']:
        drives = [4, 8, 12, 16, 24]
    elif iostandard == 'LVCMOS12':
        drives = [4, 8, 12]
    elif iostandard == 'SSTL135':
        return ['_FIXED']
    else:
        drives = [4, 8, 12, 16]

    return drives


STEPDOWN_IOSTANDARDS = ['LVCMOS12', 'LVCMOS15', 'LVCMOS18', 'SSTL135']
IBUF_LOW_PWR_SUPPORTED = ['SSTL135']


def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")
    '''
    port,site,tile,pin,slew,drive,pulltype
    di[0],IOB_X0Y107,LIOB33_X0Y107,A21,PULLDOWN
    di[10],IOB_X0Y147,LIOB33_X0Y147,F14,PULLUP
    '''
    with open('params.json', 'r') as f:
        design = json.load(f)

        diff_pairs = set()
        for d in design['tiles']:
            iostandard = verilog.unquote(d['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                diff_pairs.add(d['pair_site'])

        for d in design['tiles']:
            site = d['site']

            if skip_broken_tiles(d):
                continue

            if site in diff_pairs:
                continue

            iostandard = verilog.unquote(d['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                iostandard = iostandard[5:]

            segmk.add_site_tag(
                site, '_'.join(STEPDOWN_IOSTANDARDS) + '.STEPDOWN',
                iostandard in STEPDOWN_IOSTANDARDS)

            if 'IN_TERM' in d:
                segmaker.add_site_group_zero(
                    segmk, site, 'IN_TERM.', [
                        'NONE', 'UNTUNED_SPLIT_40', 'UNTUNED_SPLIT_50',
                        'UNTUNED_SPLIT_60'
                    ], 'NONE', d['IN_TERM'])

            if d['type'] is None:
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 0)
            elif d['type'] == 'IBUF':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'IN_DIFF', 0)

                if iostandard in IBUF_LOW_PWR_SUPPORTED:
                    segmk.add_site_tag(site, 'IBUF_LOW_PWR', d['IBUF_LOW_PWR'])
                    segmk.add_site_tag(
                        site, 'ZIBUF_LOW_PWR', 1 ^ d['IBUF_LOW_PWR'])
            elif d['type'] == 'IBUFDS':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'IN_DIFF', 1)
            elif d['type'] == 'OBUF':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'OUT_DIFF', 0)
            elif d['type'] == 'OBUFDS':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'OUT_DIFF', 1)
                segmk.add_tile_tag(d['tile'], 'OUT_TDIFF', 0)
            elif d['type'] == 'OBUFTDS':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'OUT_DIFF', 1)
                segmk.add_tile_tag(d['tile'], 'OUT_TDIFF', 1)
            elif d['type'] == 'IOBUF_INTERMDISABLE':
                segmk.add_site_tag(site, 'INOUT', 1)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)

            if d['type'] is not None:
                segmaker.add_site_group_zero(
                    segmk, site, "PULLTYPE.",
                    ("NONE", "KEEPER", "PULLDOWN", "PULLUP"), "PULLDOWN",
                    verilog.unquote(d['PULLTYPE']))

            if d['type'] in [None, 'IBUF', 'IBUFDS']:
                continue

            drive_opts = set()
            for opt in ("LVCMOS25", "LVCMOS33", "LVCMOS18", "LVCMOS15",
                        "LVCMOS12", 'LVTTL'):
                for drive_opt in ("4", "8", "12", "16", "24"):
                    if drive_opt == "16" and opt == "LVCMOS12":
                        continue

                    if drive_opt == "24" and opt not in ["LVCMOS18", 'LVTTL']:
                        continue

                    drive_opts.add(mk_drive_opt(opt, drive_opt))

            drive_opts.add(mk_drive_opt("SSTL135", None))

            segmaker.add_site_group_zero(
                segmk, site, '', drive_opts, mk_drive_opt('LVCMOS25', '12'),
                mk_drive_opt(iostandard, d['DRIVE']))

            for opt in ["SLOW", "FAST"]:
                segmk.add_site_tag(
                    site, iostandard + ".SLEW." + opt, opt == verilog.unquote(
                        d['SLEW']))

            if 'ibufdisable_wire' in d:
                segmk.add_site_tag(
                    site, 'IBUFDISABLE.I', d['ibufdisable_wire'] != '0')

            if 'intermdisable_wire' in d:
                segmk.add_site_tag(
                    site, 'INTERMDISABLE.I', d['intermdisable_wire'] != '0')

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)


if __name__ == "__main__":
    main()
