/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/frame_address.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(FrameAddressTest, YamlEncode) {
	xc7series::FrameAddress address(xc7series::BlockType::BLOCK_RAM, false,
	                                10, 0, 5);

	YAML::Node node(address);

	EXPECT_EQ(node.Tag(), "xilinx/xc7series/frame_address");
	EXPECT_EQ(node["block_type"].as<std::string>(), "BLOCK_RAM");
	EXPECT_EQ(node["row_half"].as<std::string>(), "top");
	EXPECT_EQ(node["row"].as<std::string>(), "10");
	EXPECT_EQ(node["column"].as<std::string>(), "0");
	EXPECT_EQ(node["minor"].as<std::string>(), "5");
}

TEST(FrameAddressTest, YamlDecode) {
	YAML::Node node;
	node.SetTag("xilinx/xc7series/frame_address");
	node["block_type"] = "BLOCK_RAM";
	node["row_half"] = "bottom";
	node["row"] = "0";
	node["column"] = "5";
	node["minor"] = "11";

	xc7series::FrameAddress address = node.as<xc7series::FrameAddress>();
	EXPECT_EQ(address.block_type(), xc7series::BlockType::BLOCK_RAM);
	EXPECT_TRUE(address.is_bottom_half_rows());
	EXPECT_EQ(address.row(), 0);
	EXPECT_EQ(address.column(), 5);
	EXPECT_EQ(address.minor(), 11);
}
