#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker
from prjxray import verilog
import os
import json


def bitfilter(frame, word):
    if frame < 26:
        return False

    return True


def mk_drive_opt(iostandard, drive):
    return '{}.DRIVE.I{}'.format(iostandard, drive)


def skip_broken_tiles(d):
    """ Skip tiles that appear to have bits always set.

    This is likely caused by a defect?

    """
    if os.getenv('XRAY_DATABASE') == 'artix7' and d['tile'] == 'LIOB33_X0Y43':
        return True

    return False


def drives_for_iostandard(iostandard):
    if iostandard in ['LVTTL', 'LVCMOS18']:
        drives = [4, 8, 12, 16, 24]
    elif iostandard == 'LVCMOS12':
        drives = [4, 8, 12]
    else:
        drives = [4, 8, 12, 16]

    return drives


STEPDOWN_IOSTANDARDS = ['LVCMOS12', 'LVCMOS15', 'LVCMOS18']


def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")
    '''
    port,site,tile,pin,slew,drive,pulltype
    di[0],IOB_X0Y107,LIOB33_X0Y107,A21,PULLDOWN
    di[10],IOB_X0Y147,LIOB33_X0Y147,F14,PULLUP
    '''
    with open('params.jl', 'r') as f:
        design = json.load(f)

        for d in design:
            site = d['site']

            if skip_broken_tiles(d):
                continue

            iostandard = verilog.unquote(d['IOSTANDARD'])

            stepdown = iostandard in STEPDOWN_IOSTANDARDS
            segmk.add_tile_tag(
                d['tile'], '_'.join(STEPDOWN_IOSTANDARDS), stepdown)

            if d['type'] is None:
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                for drive in drives_for_iostandard(iostandard):
                    segmk.add_site_tag(
                        site, '{}.DRIVE.I{}.IN_OUT_COMMON'.format(
                            iostandard, drive), 0)
            elif d['type'] == 'IBUF':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                for drive in drives_for_iostandard(iostandard):
                    segmk.add_site_tag(
                        site, '{}.DRIVE.I{}.IN_OUT_COMMON'.format(
                            iostandard, drive), 1)
            elif d['type'] == 'OBUF':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                for drive in drives_for_iostandard(iostandard):
                    if drive == d['DRIVE']:
                        segmk.add_site_tag(
                            site, '{}.DRIVE.I{}.IN_OUT_COMMON'.format(
                                iostandard, drive), 1)
                    else:
                        segmk.add_site_tag(
                            site, '{}.DRIVE.I{}.IN_OUT_COMMON'.format(
                                iostandard, drive), 0)
            elif d['type'] == 'IOBUF_INTERMDISABLE':
                segmk.add_site_tag(site, 'INOUT', 1)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)

            if d['type'] is not None:
                segmaker.add_site_group_zero(
                    segmk, site, "PULLTYPE.",
                    ("NONE", "KEEPER", "PULLDOWN", "PULLUP"), "PULLDOWN",
                    verilog.unquote(d['PULLTYPE']))

            if d['type'] == 'IBUF' or d['type'] is None:
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

            segmaker.add_site_group_zero(
                segmk, site, '', drive_opts, mk_drive_opt('LVCMOS25', '12'),
                mk_drive_opt(iostandard, d['DRIVE']))

            segmaker.add_site_group_zero(
                segmk, site, "SLEW.", ("SLOW", "FAST"), "FAST",
                verilog.unquote(d['SLEW']))

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
