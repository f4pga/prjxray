/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/spartan6/configuration_bus.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(ConfigurationBusTest, IsValidFrameAddress) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 1));

	spartan6::ConfigurationBus bus(addresses.begin(), addresses.end());

	EXPECT_TRUE(bus.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0)));
	EXPECT_TRUE(bus.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 1)));

	EXPECT_FALSE(bus.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2)));
}

TEST(ConfigurationBusTest, GetNextFrameAddressYieldNextAddressInBus) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 1));

	spartan6::ConfigurationBus bus(addresses.begin(), addresses.end());

	auto next_address = bus.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address, spartan6::FrameAddress(
	                             spartan6::BlockType::BLOCK_RAM, 0, 0, 1));

	next_address = bus.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address, spartan6::FrameAddress(
	                             spartan6::BlockType::BLOCK_RAM, 0, 1, 0));
}

TEST(ConfigurationBusTest, GetNextFrameAddressYieldNothingAtEndOfBus) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 1));

	spartan6::ConfigurationBus bus(addresses.begin(), addresses.end());

	EXPECT_FALSE(bus.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 1, 1)));
}
