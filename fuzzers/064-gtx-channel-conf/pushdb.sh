#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

if ! test $(find ${BUILD_DIR} -name "segdata_gtx_channel_[0123]_mid_*.txt" | wc -c) -eq 0
then
    ${XRAY_MERGEDB} gtx_channel_0_mid_left ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_1_mid_left ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_2_mid_left ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_3_mid_left ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_0_mid_left ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_1_mid_left ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_2_mid_left ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_3_mid_left ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_0_mid_right ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_1_mid_right ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_2_mid_right ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_3_mid_right ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_0_mid_right ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_1_mid_right ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_2_mid_right ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_3_mid_right ${BUILD_DIR}/mask_gtx_channelx.db
fi

if ! test $(find ${BUILD_DIR} -name "segdata_gtx_channel_[0123].txt" | wc -c) -eq 0
then
    ${XRAY_MERGEDB} gtx_channel_0 ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_1 ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_2 ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} gtx_channel_3 ${BUILD_DIR}/segbits_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_0 ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_1 ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_2 ${BUILD_DIR}/mask_gtx_channelx.db
    ${XRAY_MERGEDB} mask_gtx_channel_3 ${BUILD_DIR}/mask_gtx_channelx.db
fi
