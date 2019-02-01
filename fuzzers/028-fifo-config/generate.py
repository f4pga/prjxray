#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def add_enum_bits(segmk, params, key, options):
    for opt in options:
        segmk.add_site_tag(params['site'], '{}_{}'.format(key, opt), params[key] == opt)

def output_integer_tags(segmk, params, key, invert=False):
    site = params['site']
    bits = verilog.parse_bitstr(params[key])
    for bit, tag_val in enumerate(bits):
        if not invert:
            segmk.add_site_tag(site, "{}[{}]".format(key, len(bits)-bit-1), tag_val)
        else:
            segmk.add_site_tag(site, "Z{}[{}]".format(key, len(bits)-bit-1), 0 if tag_val else 1)

def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for tile_param in params:
        #add_enum_bits(segmk, tile_param, 'DATA_WIDTH', [4, 9, 18, 36])
        #add_enum_bits(segmk, tile_param, 'FIFO_MODE', ['FIFO18', 'FIFO18_36'])
        if tile_param['EN_SYN'] and tile_param['DATA_WIDTH'] == 4:
            output_integer_tags(segmk, tile_param, 'ALMOST_EMPTY_OFFSET', invert=True)
            output_integer_tags(segmk, tile_param, 'ALMOST_FULL_OFFSET', invert=True)
        #output_integer_tags(segmk, tile_param, 'INIT', 36, invert=True)
        #output_integer_tags(segmk, tile_param, 'SRVAL', 36, invert=True)

        for param in ('EN_SYN', 'FIRST_WORD_FALL_THROUGH'):
            segmk.add_site_tag(
                tile_param['site'], param, tile_param[param])

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
