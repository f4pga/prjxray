#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def write_ram_ext_tags(segmk, tile_param):
    for param in ["RAM_EXTENSION_A", "RAM_EXTENSION_B"]:
        set_val = tile_param[param]
        for opt in ["LOWER"]:
            segmk.add_site_tag(
                tile_param['site'], "{}_{}".format(param, opt), set_val == opt)
        segmk.add_site_tag(
            tile_param['site'], "{}_NONE_OR_UPPER".format(param, opt), set_val != "LOWER")


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for tile_param in params:
        write_ram_ext_tags(segmk, tile_param)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
