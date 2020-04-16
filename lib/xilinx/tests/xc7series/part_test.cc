/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/part.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(PartTest, IsValidFrameAddress) {
	std::vector<xc7series::FrameAddress> addresses;
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 1));

	xc7series::Part part(0x1234, addresses.begin(), addresses.end());

	EXPECT_TRUE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0)));
	EXPECT_TRUE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 0)));
	EXPECT_TRUE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2)));
	EXPECT_TRUE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 0)));
	EXPECT_TRUE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 0)));

	EXPECT_FALSE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 2)));
	EXPECT_FALSE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 2, 0)));
	EXPECT_FALSE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 2, 0, 0)));
	EXPECT_FALSE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CFG_CLB, false, 0, 0, 2)));
	EXPECT_FALSE(part.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 1, 0)));
}

TEST(PartTest, GetNextFrameAddressYieldNextAddressInPart) {
	std::vector<xc7series::FrameAddress> addresses;
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 1));

	xc7series::Part part(0x1234, addresses.begin(), addresses.end());

	auto next_address = part.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 0, 0, 1));

	next_address = part.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 0, 1, 0));

	next_address = part.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 1, 0, 0));

	next_address = part.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  true, 0, 0, 0));

	next_address = part.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::BLOCK_RAM,
	                                  false, 0, 0, 0));
}

TEST(PartTest, GetNextFrameAddressYieldNothingAtEndOfPart) {
	std::vector<xc7series::FrameAddress> addresses;
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, true, 0, 0, 1));

	xc7series::Part part(0x1234, addresses.begin(), addresses.end());

	EXPECT_FALSE(part.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2)));
}
