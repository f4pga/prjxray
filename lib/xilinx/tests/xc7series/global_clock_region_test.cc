/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/global_clock_region.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(GlobalClockRegionTest, IsValidFrameAddress) {
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

	xc7series::GlobalClockRegion global_clock_region(addresses.begin(),
	                                                 addresses.end());

	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0)));
	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 0)));
	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2)));
	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 0)));

	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 2)));
	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 2, 0)));
	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 2, 0, 0)));
	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CFG_CLB, false, 0, 0, 2)));
}

TEST(GlobalClockRegionTest,
     GetNextFrameAddressYieldNextAddressInGlobalClockRegion) {
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

	xc7series::GlobalClockRegion global_clock_region(addresses.begin(),
	                                                 addresses.end());

	auto next_address =
	    global_clock_region.GetNextFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 0, 0, 1));

	next_address =
	    global_clock_region.GetNextFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 0, 1, 0));

	next_address =
	    global_clock_region.GetNextFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 1, 0, 0));

	next_address =
	    global_clock_region.GetNextFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::BLOCK_RAM,
	                                  false, 0, 0, 2));
}

TEST(GlobalClockRegionTest,
     GetNextFrameAddressYieldNothingAtEndOfGlobalClockRegion) {
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

	xc7series::GlobalClockRegion global_clock_region(addresses.begin(),
	                                                 addresses.end());

	EXPECT_FALSE(
	    global_clock_region.GetNextFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::CLB_IO_CLK, false, 1, 0, 1)));
	EXPECT_FALSE(
	    global_clock_region.GetNextFrameAddress(xc7series::FrameAddress(
	        xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2)));
}
