/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/spartan6/block_type.h>

#include <gtest/gtest.h>

using namespace prjxray::xilinx;

TEST(BlockTypeTest, YamlEncode) {
	YAML::Node node;
	node.push_back(spartan6::BlockType::CLB_IOI_CLK);
	node.push_back(spartan6::BlockType::BLOCK_RAM);
	node.push_back(spartan6::BlockType::IOB);

	EXPECT_EQ(node[0].as<std::string>(), "CLB_IOI_CLK");
	EXPECT_EQ(node[1].as<std::string>(), "BLOCK_RAM");
	EXPECT_EQ(node[2].as<std::string>(), "IOB");
}

TEST(BlockTypeTest, YamlDecode) {
	YAML::Node node;
	node.push_back("IOB");
	node.push_back("BLOCK_RAM");
	node.push_back("CLB_IOI_CLK");

	EXPECT_EQ(node[0].as<spartan6::BlockType>(), spartan6::BlockType::IOB);
	EXPECT_EQ(node[1].as<spartan6::BlockType>(),
	          spartan6::BlockType::BLOCK_RAM);
	EXPECT_EQ(node[2].as<spartan6::BlockType>(),
	          spartan6::BlockType::CLB_IOI_CLK);
}
