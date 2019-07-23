#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import verilog
import json


def handle_data_width(segmk, d):
    if 'DATA_WIDTH' not in d:
        return

    if d['DATA_RATE_OQ'] == 'DDR':
        return

    for opt in [2, 3, 4, 5, 6, 7, 8, 10, 14]:
        segmk.add_site_tag(
            d['site'], 'OSERDESE.DATA_WIDTH.{}'.format(opt),
            d['DATA_WIDTH'] == opt)


def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")

    with open('params.jl', 'r') as f:
        design = json.load(f)

        for d in design:
            site = d['site']

            handle_data_width(segmk, d)

            if d['use_oserdese2']:
                if 'SRTYPE' in d:
                    for opt in ['ASYNC', 'SYNC']:
                        segmk.add_site_tag(
                            site, 'OSERDESE.SRTYPE.{}'.format(opt),
                            verilog.unquote(d['SRTYPE']) == opt)

                for opt in ['SDR', 'DDR']:
                    segmk.add_site_tag(
                        site, 'OSERDESE.DATA_RATE_OQ.{}'.format(opt),
                        verilog.unquote(d['DATA_RATE_OQ']) == opt)

                for opt in ['BUF', 'SDR', 'DDR']:
                    segmk.add_site_tag(
                        site, 'OSERDESE.DATA_RATE_TQ.{}'.format(opt),
                        verilog.unquote(d['DATA_RATE_TQ']) == opt)

            if d['oddr_mux_config'] != 'none':
                segmk.add_site_tag(site, 'OFF.ZINIT_Q', not d['QINIT'])
                for opt in ['OPPOSITE_EDGE', 'SAME_EDGE']:
                    segmk.add_site_tag(
                        site, 'ODDR.DDR_CLK_EDGE.{}'.format(opt),
                        verilog.unquote(d['ODDR_CLK_EDGE']) == opt)

            if d['tddr_mux_config'] != 'none':
                segmk.add_site_tag(site, 'TFF.ZINIT_Q', not d['TINIT'])
                # Note: edge settings seem to be ignored for TFF
                for opt in ['OPPOSITE_EDGE', 'SAME_EDGE']:
                    segmk.add_site_tag(
                        site, 'TDDR.DDR_CLK_EDGE.{}'.format(opt),
                        verilog.unquote(d['TDDR_CLK_EDGE']) != opt)

            # all the bellow mux configs give 0 candidates
            # this is wierd, as they are set when DDR output is used
            # something's fishy here
            if d['oddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'OMUXE2', 0)

            elif d['oddr_mux_config'] == 'none':
                segmk.add_site_tag(site, 'OMUXE2', 1)
            else:
                assert False, d['oddr_mux_config']

            if d['tddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'TMUXE2', 0)

            elif d['tddr_mux_config'] == 'none':
                segmk.add_site_tag(site, 'TMUXE2', 1)
            else:
                assert False, d['tddr_mux_config']

    segmk.compile()
    segmk.write(allow_empty=True)


if __name__ == "__main__":
    main()
