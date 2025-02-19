#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

if ! test $(find ${BUILD_DIR} -name "segdata_gtx_common_mid_right.txt" | wc -c) -eq 0
then
    ${XRAY_MERGEDB} gtx_common_mid_right ${BUILD_DIR}/segbits_gtx_common.db
    ${XRAY_MERGEDB} mask_gtx_common_mid_right ${BUILD_DIR}/mask_gtx_common.db
    ${XRAY_MERGEDB} gtx_common_mid_left ${BUILD_DIR}/segbits_gtx_common.db
    ${XRAY_MERGEDB} mask_gtx_common_mid_left ${BUILD_DIR}/mask_gtx_common.db
fi

if ! test $(find ${BUILD_DIR} -name "segdata_gtx_common.txt" | wc -c) -eq 0
then
    ${XRAY_MERGEDB} gtx_common ${BUILD_DIR}/segbits_gtx_common.db
    ${XRAY_MERGEDB} mask_gtx_common ${BUILD_DIR}/mask_gtx_common.db
fi
