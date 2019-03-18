#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker
from prjxray import verilog
import json


def bitfilter(frame, word):
    if frame < 26:
        return False

    return True

def handle_data_width(segmk, d):
    if 'DATA_WIDTH' not in d:
        return

    if verilog.unquote(d['DATA_RATE']) != 'SDR':
        return

    for opt in [2, 3, 4, 5, 6, 7, 8, 10, 14]:
        segmk.add_site_tag(
            d['site'], 'ISERDES.DATA_WIDTH.{}'.format(opt),
            d['DATA_WIDTH'] == opt)


def handle_data_rate(segmk, d):
    if 'DATA_WIDTH' not in d:
        return

    for opt in ['SDR', 'DDR']:
        segmk.add_site_tag(
            d['site'], 'ISERDES.DATA_RATE.{}'.format(opt),
            verilog.unquote(d['DATA_RATE']) == opt)


def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")

    with open('params.jl', 'r') as f:
        design = json.load(f)

        for d in design:
            site = d['site']

            handle_data_width(segmk, d)
            handle_data_rate(segmk, d)

            if 'INTERFACE_TYPE' in d:
                segmaker.add_site_group_zero(segmk, site, 'ISERDES.INTERFACE_TYPE.',
                        ('MEMORY',
                        'MEMORY_DDR3',
                        'MEMORY_QDR',
                        'NETWORKING',
                        'OVERSAMPLE',
                ), 'MEMORY', verilog.unquote(d['INTERFACE_TYPE']))

            if d['iddr_mux_config'] != 'none':
                if d['use_iserdese2']:
                    segmk.add_site_tag(site, 'ISERDES_ACTIVE', 1)
                else:
                    segmk.add_site_tag(site, 'IFF_ACTIVE', 1)
                segmk.add_site_tag(site, 'IFF.ZINIT_Q1', not d['INIT_Q1'])
                segmk.add_site_tag(site, 'IFF.ZINIT_Q2', not d['INIT_Q2'])

                if 'INIT_Q3' in d:
                    segmk.add_site_tag(site, 'IFF.ZINIT_Q3', not d['INIT_Q3'])
                    segmk.add_site_tag(site, 'IFF.ZINIT_Q4', not d['INIT_Q4'])
                    segmk.add_site_tag(
                        site, 'IFF.ZSRVAL_Q1', not d['SRVAL_Q1'])
                    segmk.add_site_tag(
                        site, 'IFF.ZSRVAL_Q2', not d['SRVAL_Q2'])
                    segmk.add_site_tag(
                        site, 'IFF.ZSRVAL_Q3', not d['SRVAL_Q3'])
                    segmk.add_site_tag(
                        site, 'IFF.ZSRVAL_Q4', not d['SRVAL_Q4'])

                if 'IS_CLK_INVERTED' in d:
                    if verilog.unquote(d['INTERFACE_TYPE']) == 'MEMORY_DDR3':
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK', not d['IS_CLK_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLKB', not d['IS_CLKB_INVERTED'])

                if 'IS_OCLK_INVERTED' in d:
                    segmk.add_site_tag(
                        site, 'IFF.ZINV_OCLK', not d['IS_OCLK_INVERTED'])

                if 'IS_C_INVERTED' in d:
                    segmk.add_site_tag(
                        site, 'IFF.ZINV_C', not d['IS_C_INVERTED'])

                segmk.add_site_tag(site, 'ZINV_D', not d['IS_D_INVERTED'])

                if 'SRTYPE' in d:
                    for opt in ['ASYNC', 'SYNC']:
                        segmk.add_site_tag(
                            site, 'IFF.SRTYPE.{}'.format(opt),
                            verilog.unquote(d['SRTYPE']) == opt)

                if 'DDR_CLK_EDGE' in d:
                    for opt in ['OPPOSITE_EDGE', 'SAME_EDGE',
                                'SAME_EDGE_PIPELINED']:
                        segmk.add_site_tag(
                            site, 'IFF.DDR_CLK_EDGE.{}'.format(opt),
                            verilog.unquote(d['DDR_CLK_EDGE']) == opt)

            ofb_used = False
            if 'OFB_USED' in d and d['OFB_USED']:
                ofb_used = True

            if d['iddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'IFFDELMUXE3.0', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.1', 1)
                segmk.add_site_tag(site, 'IFFDELMUXE3.2', 0)

                if ofb_used:
                    segmk.add_site_tag(site, 'IFFMUX.1', 1)
                    segmk.add_site_tag(site, 'IFFMUX.0', 0)
                else:
                    segmk.add_site_tag(site, 'IFFMUX.1', 0)
                    segmk.add_site_tag(site, 'IFFMUX.0', 1)
            elif d['iddr_mux_config'] == 'idelay':
                segmk.add_site_tag(site, 'IFFDELMUXE3.0', 1)
                segmk.add_site_tag(site, 'IFFDELMUXE3.1', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.2', 0)

                if ofb_used:
                    segmk.add_site_tag(site, 'IFFMUX.1', 1)
                    segmk.add_site_tag(site, 'IFFMUX.0', 0)
                else:
                    segmk.add_site_tag(site, 'IFFMUX.1', 0)
                    segmk.add_site_tag(site, 'IFFMUX.0', 1)
            elif d['iddr_mux_config'] == 'none':
                segmk.add_site_tag(site, 'IFF_ACTIVE', 0)
                segmk.add_site_tag(site, 'ISERDES_ACTIVE', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.0', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.1', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.2', 0)
                segmk.add_site_tag(site, 'IFFMUX.0', 0)
                segmk.add_site_tag(site, 'IFFMUX.1', 0)
            else:
                assert False, d['mux_config']

            if d['mux_config'] == 'direct':
                segmk.add_site_tag(site, 'O_ACTIVE', 1)
                segmk.add_site_tag(site, 'IDELMUXE3.0', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.1', 1)
                segmk.add_site_tag(site, 'IDELMUXE3.2', 0)

                if ofb_used:
                    segmk.add_site_tag(site, 'IMUX.1', 1)
                    segmk.add_site_tag(site, 'IMUX.0', 0)
                else:
                    segmk.add_site_tag(site, 'IMUX.1', 0)
                    segmk.add_site_tag(site, 'IMUX.0', 1)
            elif d['mux_config'] == 'idelay':
                segmk.add_site_tag(site, 'O_ACTIVE', 1)
                segmk.add_site_tag(site, 'IDELMUXE3.0', 1)
                segmk.add_site_tag(site, 'IDELMUXE3.1', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.2', 0)

                if ofb_used:
                    segmk.add_site_tag(site, 'IMUX.1', 1)
                    segmk.add_site_tag(site, 'IMUX.0', 0)
                else:
                    segmk.add_site_tag(site, 'IMUX.1', 0)
                    segmk.add_site_tag(site, 'IMUX.0', 1)
            elif d['mux_config'] == 'none':
                segmk.add_site_tag(site, 'O_ACTIVE', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.0', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.1', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.2', 0)
                segmk.add_site_tag(site, 'IMUX.0', 0)
                segmk.add_site_tag(site, 'IMUX.1', 0)
            else:
                assert False, d['mux_config']

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)


if __name__ == "__main__":
    main()
