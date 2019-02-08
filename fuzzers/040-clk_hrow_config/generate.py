#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for row in params:
        base_name = 'BUFHCE_X{}Y{}'.format(row['x'], row['y'])


        segmk.add_site_tag(row['site'], '{}.IN_USE'.format(base_name), row['IN_USE'])
        if not row['IN_USE']:
            continue

        segmk.add_site_tag(row['site'], '{}.INIT_OUT'.format(base_name), row['INIT_OUT'])

        # SYNC is a zero pattern
        for opt in ['ASYNC']:
            segmk.add_site_tag(row['site'], '{}.CE_TYPE.'.format(base_name) + opt, verilog.unquote(row['CE_TYPE']) == opt)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
