/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/configuration_column.h>

#include <gtest/gtest.h>
#include <prjxray/xilinx/xc7series/block_type.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <yaml-cpp/yaml.h>

using namespace prjxray::xilinx;

TEST(ConfigurationColumnTest, IsValidFrameAddress) {
	xc7series::ConfigurationColumn column(10);

	// Inside this column.
	EXPECT_TRUE(column.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 3)));
	// Past this column's frame width.
	EXPECT_FALSE(column.IsValidFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 10)));
}

TEST(ConfigurationColumnTest, GetNextFrameAddressYieldNextAddressInColumn) {
	xc7series::ConfigurationColumn column(10);

	auto next_address = column.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 3));
	EXPECT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK,
	                                  false, 1, 2, 4));
}

TEST(ConfigurationColumnTest, GetNextFrameAddressYieldNothingAtEndOfColumn) {
	xc7series::ConfigurationColumn column(10);

	EXPECT_FALSE(column.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 9)));
}

TEST(ConfigurationColumnTest, GetNextFrameAddressYieldNothingOutsideColumn) {
	xc7series::ConfigurationColumn column(10);

	// Just past last frame in column.
	EXPECT_FALSE(column.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 10)));
}

TEST(ConfigurationColumnTest, YamlEncodeTest) {
	xc7series::ConfigurationColumn column(10);

	YAML::Node node(column);
	EXPECT_TRUE(node["frame_count"]);
	EXPECT_EQ(node["frame_count"].as<int>(), 10);
}

TEST(ConfigurationColumnTest, YAMLDecodeTest) {
	YAML::Node node;
	node.SetTag("xilinx/xc7series/configuration_column");
	node["frame_count"] = 10;

	auto column = node.as<xc7series::ConfigurationColumn>();
	EXPECT_TRUE(column.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 8)));
	EXPECT_FALSE(column.GetNextFrameAddress(xc7series::FrameAddress(
	    xc7series::BlockType::CLB_IO_CLK, false, 1, 2, 9)));
}
