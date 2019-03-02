""" Sanity checks FASM output from IOB fuzzer.

The IOB fuzzer is fairly complicated, and it's output is hard to verify by
inspected.  For this reason, check_results.py was written to compare the
specimen's generated and their FASM output.  The FASM output does pose a
chicken and egg issue.  The test procedure is a follows:

1. Build the database (e.g. make -j<N> run)
2. Build the database again (e.g. make -j<N> run)
3. Run check_results.py

The second time that the database is run, the FASM files in the specimen's
will have the bits documented by fuzzer.

"""
import os
import os.path
from prjxray import verilog
import json
import generate


def process_parts(parts):
    if parts[0] == 'INOUT':
        yield 'type', 'IOBUF_INTERMDISABLE'

    if parts[0] == 'IN_ONLY':
        yield 'type', 'IBUF'

    if parts[0] == 'SLEW':
        yield 'SLEW', verilog.quote(parts[1])

    if parts[0] == 'PULLTYPE':
        yield 'PULLTYPE', verilog.quote(parts[1])

    if len(parts) > 1 and parts[1] == 'IN':
        yield 'IOSTANDARDS', parts[0].split('_')

    if len(parts) > 1 and parts[1] == 'DRIVE':
        yield 'IOSTANDARDS', parts[0].split('_')
        yield 'DRIVES', parts[2].split('_')


def create_sites_from_fasm(root):
    sites = {}

    with open(os.path.join(root, 'design.fasm')) as f:
        for l in f:
            if 'IOB33' not in l:
                continue

            parts = l.strip().split('.')
            tile = parts[0]
            site = parts[1]
            if (tile, site) not in sites:
                sites[(tile, site)] = {
                    'tile': tile,
                    'site_key': site,
                }

            for key, value in process_parts(parts[2:]):
                sites[(tile, site)][key] = value

    for key in sites:
        if 'type' not in sites[key]:
            if 'IOSTANDARDS' not in sites[key]:
                sites[key]['type'] = None
            else:
                assert 'IOSTANDARDS' in sites[key], sites[key]
                assert 'DRIVES' in sites[key]
                sites[key]['type'] = "OBUF"

    return sites


def process_specimen(root):
    sites = create_sites_from_fasm(root)

    with open(os.path.join(root, 'params.jl')) as f:
        params = json.load(f)

    for p in params:
        tile = p['tile']
        site = p['site']
        site_y = int(site[site.find('Y') + 1:]) % 2

        if generate.skip_broken_tiles(p):
            continue

        site_key = 'IOB_Y{}'.format(site_y)

        if (tile, site_key) not in sites:
            assert p['type'] is None, p
            continue

        site_from_fasm = sites[(tile, site_key)]

        assert p['type'] == site_from_fasm['type'], (
            tile, site_key, p, site_from_fasm)

        if p['type'] is None:
            continue

        assert p['PULLTYPE'] == site_from_fasm['PULLTYPE'], (
            tile, site_key, p, site_from_fasm)

        assert verilog.unquote(
            p['IOSTANDARD']) in site_from_fasm['IOSTANDARDS'], (
                tile, site_key, p, site_from_fasm)

        if p['type'] != 'IBUF':
            assert p['SLEW'] == site_from_fasm['SLEW'], (
                tile, site_key, p, site_from_fasm)

            assert 'I{}'.format(p['DRIVE']) in site_from_fasm['DRIVES'], (
                tile, site_key, p, site_from_fasm)


def main():
    for root, dirs, files in os.walk('build'):
        if os.path.basename(root).startswith('specimen_'):
            print('Processing', os.path.basename(root))
            process_specimen(root)

    print('No errors found!')


if __name__ == "__main__":
    main()
