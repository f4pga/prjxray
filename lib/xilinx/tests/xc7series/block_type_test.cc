/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/block_type.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(BlockTypeTest, YamlEncode) {
	YAML::Node node;
	node.push_back(xc7series::BlockType::CLB_IO_CLK);
	node.push_back(xc7series::BlockType::BLOCK_RAM);
	node.push_back(xc7series::BlockType::CFG_CLB);

	EXPECT_EQ(node[0].as<std::string>(), "CLB_IO_CLK");
	EXPECT_EQ(node[1].as<std::string>(), "BLOCK_RAM");
	EXPECT_EQ(node[2].as<std::string>(), "CFG_CLB");
}

TEST(BlockTypeTest, YamlDecode) {
	YAML::Node node;
	node.push_back("CFG_CLB");
	node.push_back("BLOCK_RAM");
	node.push_back("CLB_IO_CLK");

	EXPECT_EQ(node[0].as<xc7series::BlockType>(),
	          xc7series::BlockType::CFG_CLB);
	EXPECT_EQ(node[1].as<xc7series::BlockType>(),
	          xc7series::BlockType::BLOCK_RAM);
	EXPECT_EQ(node[2].as<xc7series::BlockType>(),
	          xc7series::BlockType::CLB_IO_CLK);
}
