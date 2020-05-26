/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/spartan6/configuration_row.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(RowTest, IsValidFrameAddress) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));

	spartan6::Row row(addresses.begin(), addresses.end());

	EXPECT_TRUE(row.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0)));
	EXPECT_TRUE(row.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0)));
	EXPECT_TRUE(row.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2)));

	EXPECT_FALSE(row.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 2)));
	EXPECT_FALSE(row.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 2, 0)));
}

TEST(RowTest, GetNextFrameAddressYieldNextAddressInRow) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));

	spartan6::Row row(addresses.begin(), addresses.end());

	auto next_address = row.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(
	    *next_address,
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));

	next_address = row.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(
	    *next_address,
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));

	// Rows have unique behavior for GetNextFrameAddress() at the end of a
	// bus. Since the addresses need to be returned in numerically
	// increasing order, all of the rows need to be returned before moving
	// to a different bus.  That means that Row::GetNextFrameAddress() needs
	// to return no object at the end of a bus and let the caller use that
	// as a signal to try the next row.
	next_address = row.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	EXPECT_FALSE(next_address);

	next_address = row.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address, spartan6::FrameAddress(
	                             spartan6::BlockType::BLOCK_RAM, 0, 0, 2));

	next_address = row.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));
	EXPECT_FALSE(next_address);
}

TEST(RowTest, GetNextFrameAddressYieldNothingAtEndOfRow) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));

	spartan6::Row row(addresses.begin(), addresses.end());

	EXPECT_FALSE(row.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2)));
}
