/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/bit_ops.h>

#include <gtest/gtest.h>

TEST(BitMaskTest, Bit0) {
	uint32_t expected = prjxray::bit_mask<uint32_t>(0);
	EXPECT_EQ(static_cast<uint32_t>(0x1), expected);
}

TEST(BitMaskTest, Bit3) {
	uint32_t expected = prjxray::bit_mask<uint32_t>(3);
	EXPECT_EQ(static_cast<uint32_t>(0x8), expected);
}

TEST(BitMaskRange, SingleBit) {
	uint32_t expected = prjxray::bit_mask_range<uint32_t>(23, 23);
	EXPECT_EQ(static_cast<uint32_t>(0x800000), expected);
}

TEST(BitMaskRange, DownToZero) {
	uint32_t expected = prjxray::bit_mask_range<uint32_t>(7, 0);
	EXPECT_EQ(static_cast<uint32_t>(0xFF), expected);
}

TEST(BitMaskRange, MiddleBits) {
	uint32_t expected = prjxray::bit_mask_range<uint32_t>(18, 8);
	EXPECT_EQ(static_cast<uint32_t>(0x7FF00), expected);
}

TEST(BitFieldGetTest, OneSelectedBit) {
	uint32_t expected = prjxray::bit_field_get(0xFFFFFFFF, 23, 23);
	EXPECT_EQ(static_cast<uint32_t>(1), expected);
}

TEST(BitFieldGetTest, SelectDownToZero) {
	uint32_t expected = prjxray::bit_field_get(0xFFCCBBAA, 7, 0);
	EXPECT_EQ(static_cast<uint32_t>(0xAA), expected);
}

TEST(BitFieldGetTest, SelectMidway) {
	uint32_t expected = prjxray::bit_field_get(0xFFCCBBAA, 18, 8);
	EXPECT_EQ(static_cast<uint32_t>(0x4BB), expected);
}

TEST(BitFieldSetTest, WriteOneBit) {
	uint32_t actual = prjxray::bit_field_set(
	    static_cast<uint32_t>(0x0), 23, 23, static_cast<uint32_t>(0x1));
	EXPECT_EQ(actual, static_cast<uint32_t>(0x800000));
}

TEST(BitFieldSetTest, WriteOneBitWithOutOfRangeValue) {
	uint32_t actual = prjxray::bit_field_set(
	    static_cast<uint32_t>(0x0), 23, 23, static_cast<uint32_t>(0x3));
	EXPECT_EQ(actual, static_cast<uint32_t>(0x800000));
}

TEST(BitFieldSetTest, WriteMultipleBits) {
	uint32_t actual = prjxray::bit_field_set(
	    static_cast<uint32_t>(0x0), 18, 8, static_cast<uint32_t>(0x123));
	EXPECT_EQ(actual, static_cast<uint32_t>(0x12300));
}

TEST(BitFieldSetTest, WriteMultipleBitsWithOutOfRangeValue) {
	uint32_t actual = prjxray::bit_field_set(
	    static_cast<uint32_t>(0x0), 18, 8, static_cast<uint32_t>(0x1234));
	EXPECT_EQ(actual, static_cast<uint32_t>(0x23400));
}
