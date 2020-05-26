#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from prjxray.segmaker import Segmaker
from prjxray import verilog
import json

# Set to true to enable additional tags useful for tracing bit toggles.
DEBUG_FUZZER = False


def bitfilter(frame, word):
    if frame < 25 or frame > 31:
        return False

    return True


def handle_data_width(segmk, d):
    if 'DATA_WIDTH' not in d:
        return

    site = d['ilogic_loc']

    # It appears several widths end up with the same bitstream pattern.
    # This groups those widths together for documentation.
    widths = [
        [2],
        [3],
        [4, 6],
        [5, 7],
        [8],
        [10],
        [14],
    ]

    width_map = {}

    for ws in widths:
        for w in ws:
            width_map[w] = 'W{}'.format('_'.join(map(str, ws)))

    zero_opt = 2
    W_OPT_ZERO = width_map[zero_opt]
    if d['DATA_WIDTH'] == zero_opt:
        segmk.add_site_tag(site, 'ISERDES.DATA_WIDTH.{}'.format(W_OPT_ZERO), 1)

        for opt in width_map.values():
            if opt == W_OPT_ZERO:
                continue

            segmk.add_site_tag(site, 'ISERDES.DATA_WIDTH.{}'.format(opt), 0)
    else:
        w_opt = width_map[d['DATA_WIDTH']]
        if w_opt != W_OPT_ZERO:
            segmk.add_site_tag(
                site, 'ISERDES.DATA_WIDTH.{}'.format(W_OPT_ZERO), 0)
            segmk.add_site_tag(site, 'ISERDES.DATA_WIDTH.{}'.format(w_opt), 1)


def handle_data_rate(segmk, d):
    if 'DATA_WIDTH' not in d:
        return

    site = d['ilogic_loc']

    for opt in ['SDR', 'DDR']:
        segmk.add_site_tag(
            site, 'ISERDES.DATA_RATE.{}'.format(opt),
            verilog.unquote(d['DATA_RATE']) == opt)


def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")

    with open('params.jl', 'r') as f:
        design = json.load(f)

        for d in design:
            site = d['ilogic_loc']

            handle_data_width(segmk, d)
            handle_data_rate(segmk, d)

            segmk.add_site_tag(site, 'ISERDES.IN_USE', d['use_iserdese2'])

            if 'NUM_CE' in d:
                segmk.add_site_tag(site, 'ISERDES.NUM_CE.N2', d['NUM_CE'] == 2)

            segmk.add_site_tag(
                site, 'IDDR_OR_ISERDES.IN_USE', d['use_iserdese2']
                or d['iddr_mux_config'] != 'none')

            if 'INTERFACE_TYPE' in d:
                for opt in (
                        'MEMORY',
                        'MEMORY_DDR3',
                        'MEMORY_QDR',
                        'NETWORKING',
                        'OVERSAMPLE',
                ):
                    segmk.add_site_tag(
                        site, 'ISERDES.INTERFACE_TYPE.{}'.format(opt),
                        opt == verilog.unquote(d['INTERFACE_TYPE']))
                    segmk.add_site_tag(
                        site, 'ISERDES.INTERFACE_TYPE.Z_{}'.format(opt),
                        opt != verilog.unquote(d['INTERFACE_TYPE']))

                segmk.add_site_tag(
                    site, 'ISERDES.INTERFACE_TYPE.NOT_MEMORY',
                    'MEMORY' not in verilog.unquote(d['INTERFACE_TYPE']))

            if d['iddr_mux_config'] != 'none':
                segmk.add_site_tag(site, 'IFF.ZINIT_Q1', not d['INIT_Q1'])
                segmk.add_site_tag(site, 'IFF.ZINIT_Q2', not d['INIT_Q2'])

                if 'DYN_CLKDIV_INV_EN' in d:
                    segmk.add_site_tag(
                        site, 'DYN_CLKDIV_INV_EN',
                        verilog.unquote(d['DYN_CLKDIV_INV_EN']) == 'TRUE')

                if 'DYN_CLK_INV_EN' in d:
                    segmk.add_site_tag(
                        site, 'DYN_CLK_INV_EN',
                        verilog.unquote(d['DYN_CLK_INV_EN']) == 'TRUE')

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

                if 'IS_CLK_INVERTED' in d and not d['DISABLE_CLOCKS']:
                    if verilog.unquote(d['INTERFACE_TYPE']) == 'MEMORY_DDR3':
                        segmk.add_site_tag(
                            site, 'IFF.INV_CLK', d['IS_CLK_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.INV_CLKB', d['IS_CLKB_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK', not d['IS_CLK_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLKB', not d['IS_CLKB_INVERTED'])

                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK_XOR',
                            d['IS_CLK_INVERTED'] ^ d['IS_CLKB_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK_NXOR',
                            not (d['IS_CLK_INVERTED'] ^ d['IS_CLKB_INVERTED']))

                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK_OR', d['IS_CLK_INVERTED']
                            or d['IS_CLKB_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK_NOR', not (
                                d['IS_CLK_INVERTED'] or d['IS_CLKB_INVERTED']))
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK_AND', d['IS_CLK_INVERTED']
                            and d['IS_CLKB_INVERTED'])
                        segmk.add_site_tag(
                            site, 'IFF.ZINV_CLK_NAND', not (
                                d['IS_CLK_INVERTED']
                                and d['IS_CLKB_INVERTED']))

                if 'IS_OCLK_INVERTED' in d and not d['DISABLE_CLOCKS']:
                    segmk.add_site_tag(
                        site, 'IFF.INV_OCLK', d['IS_OCLK_INVERTED'])
                    segmk.add_site_tag(
                        site, 'IFF.ZINV_OCLK', not d['IS_OCLK_INVERTED'])
                    segmk.add_site_tag(
                        site, 'IFF.INV_OCLKB', d['IS_OCLKB_INVERTED'])
                    segmk.add_site_tag(
                        site, 'IFF.ZINV_OCLKB', not d['IS_OCLKB_INVERTED'])

                if 'IS_CLKDIV_INVERTED' in d and not d['DISABLE_CLOCKS'] and \
                    verilog.unquote(d['INTERFACE_TYPE']) == 'MEMORY':
                    segmk.add_site_tag(
                        site, 'IFF.INV_CLKDIV', d['IS_CLKDIV_INVERTED'])
                    segmk.add_site_tag(
                        site, 'IFF.ZINV_CLKDIV', not d['IS_CLKDIV_INVERTED'])

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

            if d['iddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'IFFDELMUXE3.P0', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.P1', 1)
                segmk.add_site_tag(site, 'IFFDELMUXE3.P2', 0)
            elif d['iddr_mux_config'] == 'idelay':
                segmk.add_site_tag(site, 'IFFDELMUXE3.P0', 1)
                segmk.add_site_tag(site, 'IFFDELMUXE3.P1', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.P2', 0)
            elif d['iddr_mux_config'] == 'none':
                segmk.add_site_tag(site, 'IFFDELMUXE3.P0', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.P1', 0)
                segmk.add_site_tag(site, 'IFFDELMUXE3.P2', 0)
            else:
                assert False, d['mux_config']

            if d['mux_config'] == 'direct':
                segmk.add_site_tag(site, 'IDELMUXE3.P0', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.P1', 1)
                segmk.add_site_tag(site, 'IDELMUXE3.P2', 0)

            elif d['mux_config'] == 'idelay':
                segmk.add_site_tag(site, 'IDELMUXE3.P0', 1)
                segmk.add_site_tag(site, 'IDELMUXE3.P1', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.P2', 0)

            elif d['mux_config'] == 'none':
                segmk.add_site_tag(site, 'IDELMUXE3.P0', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.P1', 0)
                segmk.add_site_tag(site, 'IDELMUXE3.P2', 0)
            else:
                assert False, d['mux_config']

            if DEBUG_FUZZER:
                for k in d:
                    segmk.add_site_tag(
                        site, 'param_' + k + '_' + str(d[k]).replace(
                            ' ', '').replace('\n', ''), 1)

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)


if __name__ == "__main__":
    main()
