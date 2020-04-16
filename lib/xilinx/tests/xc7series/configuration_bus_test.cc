/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/configuration_bus.h>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(ConfigurationBusTest, IsValidFrameAddress) {
	std::vector<xc7series::FrameAddress> addresses;
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 1));

	xc7series::ConfigurationBus bus(addresses.begin(), addresses.end());

	EXPECT_TRUE(bus.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0)));
	EXPECT_TRUE(bus.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 1)));

	EXPECT_FALSE(bus.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 2)));
}

TEST(ConfigurationBusTest, GetNextFrameAddressYieldNextAddressInBus) {
	std::vector<xc7series::FrameAddress> addresses;
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 1));

	xc7series::ConfigurationBus bus(addresses.begin(), addresses.end());

	auto next_address = bus.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::BLOCK_RAM,
	                                  false, 0, 0, 1));

	next_address = bus.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::BLOCK_RAM,
	                                  false, 0, 1, 0));
}

TEST(ConfigurationBusTest, GetNextFrameAddressYieldNothingAtEndOfBus) {
	std::vector<xc7series::FrameAddress> addresses;
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 0));
	addresses.push_back(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 1));

	xc7series::ConfigurationBus bus(addresses.begin(), addresses.end());

	EXPECT_FALSE(bus.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::BLOCK_RAM, false, 0, 1, 1)));
}
