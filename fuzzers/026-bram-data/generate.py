#!/usr/bin/env python3

import json
from prjxray.segmaker import Segmaker

BITS_PER_PARAM = 256
NUM_INITP_PARAMS = 8
NUM_INIT_PARAMS = 0x40
BITS_PER_SITE = BITS_PER_PARAM * (NUM_INITP_PARAMS + NUM_INIT_PARAMS)


def main():
    segmk = Segmaker("design.bits")
    segmk.set_def_bt('BLOCK_RAM')

    print("Loading tags")
    '''
    '''

    with open('params.json') as f:
        params = json.load(f)

    for param in params:
        for initp in range(NUM_INITP_PARAMS):
            p = 'INITP_{:02X}'.format(initp)
            val = param[p]
            for bit in range(BITS_PER_PARAM):
                segmk.add_site_tag(
                    param['site'], "{p}[{bit:03d}]".format(
                        p=p,
                        bit=bit,
                    ), val & (1 << bit) != 0)

        for init in range(NUM_INIT_PARAMS):
            p = 'INIT_{:02X}'.format(init)
            val = param[p]
            for bit in range(BITS_PER_PARAM):
                segmk.add_site_tag(
                    param['site'], "{p}[{bit:03d}]".format(
                        p=p,
                        bit=bit,
                    ), val & (1 << bit) != 0)

    segmk.compile()
    segmk.write()


if __name__ == "__main__":
    main()
