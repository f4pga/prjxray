/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/ecc.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(IcapEccTest, SimpleTests) {
	// ECC for Zero Data
	EXPECT_EQ(xc7series::icap_ecc(0, 0, 0), (uint32_t)0x0);
	// 0x1320 - 0x13FF (avoid lower)
	EXPECT_EQ(xc7series::icap_ecc(0, 1, 0), (uint32_t)0x1320);
	// 0x1420 - 0x17FF (avoid 0x400)
	EXPECT_EQ(xc7series::icap_ecc(0x7, 1, 0), (uint32_t)0x1420);
	// 0x1820 - 0x1FFF (avoid 0x800)
	EXPECT_EQ(xc7series::icap_ecc(0x26, 1, 0), (uint32_t)0x1820);
	// Masked ECC Value
	EXPECT_EQ(xc7series::icap_ecc(0x32, ~0, 0), (uint32_t)0x000019AC);
	// Final ECC Parity
	EXPECT_EQ(xc7series::icap_ecc(0x64, 0, 1), (uint32_t)0x00001001);
}
