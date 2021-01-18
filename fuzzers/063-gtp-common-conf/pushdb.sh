#!/bin/bash

if ! test $(find . -name "segdata_gtp_common_mid_right.txt" | wc -c) -eq 0
then
    ${XRAY_MERGEDB} gtp_common_mid_right build/segbits_gtp_common.db
    ${XRAY_MERGEDB} mask_gtp_common_mid_right build/mask_gtp_common.db
    ${XRAY_MERGEDB} gtp_common_mid_left build/segbits_gtp_common.db
    ${XRAY_MERGEDB} mask_gtp_common_mid_left build/mask_gtp_common.db
fi

if ! test $(find . -name "segdata_gtp_common.txt" | wc -c) -eq 0
then
    ${XRAY_MERGEDB} gtp_common build/segbits_gtp_common.db
    ${XRAY_MERGEDB} mask_gtp_common build/mask_gtp_common.db
fi
