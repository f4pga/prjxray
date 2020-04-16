/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/big_endian_span.h>

#include <cstdint>
#include <vector>

#include <gtest/gtest.h>

TEST(BigEndianSpanTest, Read32WithEmptySpan) {
	std::vector<uint8_t> bytes;
	auto words = prjxray::make_big_endian_span<uint32_t>(bytes);
	EXPECT_EQ(words.size(), static_cast<size_t>(0));
}

TEST(BigEndianSpanTest, Read32WithTooFewBytes) {
	std::vector<uint8_t> bytes{0x0, 0x1, 0x2};
	auto words = prjxray::make_big_endian_span<uint32_t>(bytes);
	EXPECT_EQ(words.size(), static_cast<size_t>(0));
}

TEST(BigEndianSpanTest, Read32WithExactBytes) {
	std::vector<uint8_t> bytes{0x0, 0x1, 0x2, 0x3};
	auto words = prjxray::make_big_endian_span<uint32_t>(bytes);
	ASSERT_EQ(words.size(), static_cast<size_t>(1));
	EXPECT_EQ(words[0], static_cast<uint32_t>(0x00010203));
}

TEST(BigEndianSpanTest, Read32WithMultipleWords) {
	std::vector<uint8_t> bytes{0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7};
	auto words = prjxray::make_big_endian_span<uint32_t>(bytes);
	ASSERT_EQ(words.size(), static_cast<size_t>(2));
	EXPECT_EQ(words[0], static_cast<uint32_t>(0x00010203));
	EXPECT_EQ(words[1], static_cast<uint32_t>(0x04050607));
}

TEST(BigEndianSpanTest, Write32) {
	std::vector<uint8_t> bytes{0x0, 0x1, 0x2, 0x3};
	auto words = prjxray::make_big_endian_span<uint32_t>(bytes);
	words[0] = 0x04050607;

	std::vector<uint8_t> expected{0x4, 0x5, 0x6, 0x7};
	EXPECT_EQ(bytes, expected);
}
