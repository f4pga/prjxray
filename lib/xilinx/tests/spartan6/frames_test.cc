/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <vector>

#include <gtest/gtest.h>

#include <prjxray/xilinx/frames.h>
#include <prjxray/xilinx/spartan6/part.h>

using namespace prjxray::xilinx;
TEST(FramesTest, FillInMissingFrames) {
	std::vector<spartan6::FrameAddress> test_part_addresses = {
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0),
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1),
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 2),
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 3),
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 4)};

	spartan6::Part test_part(0x1234, test_part_addresses);

	Frames<Spartan6> frames;
	frames.getFrames().emplace(std::make_pair(
	    spartan6::FrameAddress(2), std::vector<uint32_t>(65, 0xCC)));
	frames.getFrames().emplace(std::make_pair(
	    spartan6::FrameAddress(3), std::vector<uint32_t>(65, 0xDD)));
	frames.getFrames().emplace(std::make_pair(
	    spartan6::FrameAddress(4), std::vector<uint32_t>(65, 0xEE)));

	ASSERT_EQ(frames.getFrames().size(), 3);
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[2]),
	          std::vector<uint32_t>(65, 0xCC));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[3]),
	          std::vector<uint32_t>(65, 0xDD));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[4]),
	          std::vector<uint32_t>(65, 0xEE));

	frames.addMissingFrames(test_part);

	ASSERT_EQ(frames.getFrames().size(), 5);
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[0]),
	          std::vector<uint32_t>(65, 0));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[1]),
	          std::vector<uint32_t>(65, 0));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[2]),
	          std::vector<uint32_t>(65, 0xCC));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[3]),
	          std::vector<uint32_t>(65, 0xDD));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[4]),
	          std::vector<uint32_t>(65, 0xEE));
}
