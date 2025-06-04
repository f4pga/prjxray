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
    if frame < 30 or frame > 37:
        return False

    return True


def handle_data_width(segmk, d):
    if 'DATA_WIDTH' not in d:
        return

    site = d['ologic_loc']

    data_rate = verilog.unquote(d['DATA_RATE_OQ'])
    segmk.add_site_tag(
        site, 'OSERDES.DATA_WIDTH.{}.W{}'.format(data_rate, d['DATA_WIDTH']),
        1)


def no_oserdes(segmk, site):
    for mode in ['SDR', 'DDR']:
        if mode == 'SDR':
            widths = [2, 3, 4, 5, 6, 7, 8]
        else:
            assert mode == 'DDR'
            widths = [4, 6, 8, 10, 14]

        for opt in widths:
            segmk.add_site_tag(
                site, 'OSERDES.DATA_WIDTH.{}.W{}'.format(mode, opt), 0)


def main():
    print("Loading tags")
    segmk = Segmaker("design.bits")

    with open('params.jl', 'r') as f:
        design = json.load(f)

        for d in design:
            site = d['ologic_loc']

            handle_data_width(segmk, d)

            segmk.add_site_tag(site, 'OSERDES.IN_USE', d['use_oserdese2'])

            if d['use_oserdese2']:
                segmk.add_site_tag(site, 'OQUSED', 1)

                for opt in ['SDR', 'DDR']:
                    segmk.add_site_tag(
                        site, 'OSERDES.DATA_RATE_OQ.{}'.format(opt),
                        verilog.unquote(d['DATA_RATE_OQ']) == opt)

                data_rate_tq = verilog.unquote(d['DATA_RATE_TQ'])
                segmk.add_site_tag(
                    site, 'OSERDES.DATA_RATE_TQ.{}'.format(data_rate_tq), 1)
                for opt in ['BUF', 'SDR', 'DDR']:
                    segmk.add_site_tag(
                        site, 'OSERDES.DATA_RATE_TQ.{}'.format(opt),
                        opt == data_rate_tq)

                for opt in ['SRVAL_OQ', 'SRVAL_TQ', 'INIT_OQ', 'INIT_TQ']:
                    segmk.add_site_tag(site, opt, d[opt])
                    segmk.add_site_tag(site, 'Z' + opt, 1 ^ d[opt])

                for opt in ['CLK', 'CLKDIV']:
                    if d['{}_USED'.format(opt)]:
                        k = 'IS_{}_INVERTED'.format(opt)
                        segmk.add_site_tag(site, k, d[k])
                        segmk.add_site_tag(
                            site, 'ZINV_{}'.format(opt), 1 ^ d[k])

                if d['io']:
                    for idx in range(4):
                        k = 'IS_T{}_INVERTED'.format(idx + 1)
                        segmk.add_site_tag(site, k, d[k])
                        segmk.add_site_tag(
                            site, 'ZINV_T{}'.format(idx + 1), 1 ^ d[k])

                for idx in range(8):
                    k = 'IS_D{}_INVERTED'.format(idx + 1)
                    segmk.add_site_tag(site, k, d[k])
                    segmk.add_site_tag(
                        site, 'ZINV_D{}'.format(idx + 1), 1 ^ d[k])

                for tristate_width in [1, 4]:
                    segmk.add_site_tag(
                        site,
                        'OSERDES.TRISTATE_WIDTH.W{}'.format(tristate_width),
                        d['TRISTATE_WIDTH'] == tristate_width)

                for opt in ['MASTER', 'SLAVE']:
                    segmk.add_site_tag(
                        site, 'OSERDES.SERDES_MODE.{}'.format(opt),
                        opt == verilog.unquote(d['OSERDES_MODE']))

            if 'o_sr_used' in d:
                if d['o_sr_used'] in ['S', 'R']:
                    segmk.add_site_tag(site, 'ODDR.SRUSED', 1)
                    segmk.add_site_tag(site, 'ODDR.ZSRUSED', 0)
                else:
                    assert d['o_sr_used'] == 'None'
                    segmk.add_site_tag(site, 'ODDR.SRUSED', 0)
                    segmk.add_site_tag(site, 'ODDR.ZSRUSED', 1)

            if 't_sr_used' in d:
                if d['t_sr_used'] in ['S', 'R']:
                    segmk.add_site_tag(site, 'TDDR.SRUSED', 1)
                    segmk.add_site_tag(site, 'TDDR.ZSRUSED', 0)
                else:
                    assert d['t_sr_used'] == 'None'
                    segmk.add_site_tag(site, 'TDDR.SRUSED', 0)
                    segmk.add_site_tag(site, 'TDDR.ZSRUSED', 1)

            if d['oddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'ODDR_TDDR.IN_USE', 1)

            if d['tddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'ODDR_TDDR.IN_USE', 1)

            if d['oddr_mux_config'] == 'direct' and d[
                    'tddr_mux_config'] == 'direct':
                segmk.add_site_tag(site, 'ZINV_CLK', 1 ^ d['IS_CLK_INVERTED'])

                if d['IS_CLK_INVERTED'] == 0:
                    for opt in ['OPPOSITE_EDGE', 'SAME_EDGE']:
                        segmk.add_site_tag(
                            site, 'ODDR.DDR_CLK_EDGE.{}'.format(opt),
                            verilog.unquote(d['ODDR_CLK_EDGE']) == opt)

                segmk.add_site_tag(
                    site, 'TDDR.DDR_CLK_EDGE.INV',
                    d['ODDR_CLK_EDGE'] != d['TDDR_CLK_EDGE'])
                segmk.add_site_tag(
                    site, 'TDDR.DDR_CLK_EDGE.ZINV',
                    d['ODDR_CLK_EDGE'] == d['TDDR_CLK_EDGE'])

                if 'SRTYPE' in d:
                    for opt in ['ASYNC', 'SYNC']:
                        segmk.add_site_tag(
                            site, 'OSERDES.SRTYPE.{}'.format(opt),
                            verilog.unquote(d['SRTYPE']) == opt)

                for opt in ['ASYNC', 'SYNC']:
                    segmk.add_site_tag(
                        site, 'OSERDES.TSRTYPE.{}'.format(opt),
                        verilog.unquote(d['TSRTYPE']) == opt)

            if not d['use_oserdese2']:
                no_oserdes(segmk, site)
                if d['oddr_mux_config'] == 'lut':
                    segmk.add_site_tag(site, 'ODDR_TDDR.IN_USE', 0)
                    segmk.add_site_tag(site, 'OMUX.D1', 1)
                    segmk.add_site_tag(site, 'OQUSED', 1)
                elif d['oddr_mux_config'] == 'direct':
                    segmk.add_site_tag(site, 'OMUX.D1', 0)
                elif d['oddr_mux_config'] == 'none' and not d['io']:
                    segmk.add_site_tag(site, 'OQUSED', 0)

            segmk.add_site_tag(site, 'TQUSED', d['io'])

            if DEBUG_FUZZER:
                for k in d:
                    segmk.add_site_tag(
                        site, 'param_' + k + '_' + str(d[k]).replace(
                            ' ', '').replace('\n', ''), 1)

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)


if __name__ == "__main__":
    main()
