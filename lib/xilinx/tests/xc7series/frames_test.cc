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

#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/frames.h>
#include <prjxray/xilinx/xc7series/part.h>

using namespace prjxray::xilinx;

TEST(FramesTest, FillInMissingFrames) {
	std::vector<xc7series::FrameAddress> test_part_addresses = {
	    xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK, false, 0,
	                            0, 0),
	    xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK, false, 0,
	                            0, 1),
	    xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK, false, 0,
	                            0, 2),
	    xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK, false, 0,
	                            0, 3),
	    xc7series::FrameAddress(xc7series::BlockType::CLB_IO_CLK, false, 0,
	                            0, 4)};

	xc7series::Part test_part(0x1234, test_part_addresses);

	Frames<Series7> frames;
	frames.getFrames().emplace(std::make_pair(
	    xc7series::FrameAddress(2), std::vector<uint32_t>(101, 0xCC)));
	frames.getFrames().emplace(std::make_pair(
	    xc7series::FrameAddress(3), std::vector<uint32_t>(101, 0xDD)));
	frames.getFrames().emplace(std::make_pair(
	    xc7series::FrameAddress(4), std::vector<uint32_t>(101, 0xEE)));

	ASSERT_EQ(frames.getFrames().size(), 3);
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[2]),
	          std::vector<uint32_t>(101, 0xCC));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[3]),
	          std::vector<uint32_t>(101, 0xDD));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[4]),
	          std::vector<uint32_t>(101, 0xEE));

	frames.addMissingFrames(test_part);

	ASSERT_EQ(frames.getFrames().size(), 5);
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[0]),
	          std::vector<uint32_t>(101, 0));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[1]),
	          std::vector<uint32_t>(101, 0));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[2]),
	          std::vector<uint32_t>(101, 0xCC));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[3]),
	          std::vector<uint32_t>(101, 0xDD));
	EXPECT_EQ(frames.getFrames().at(test_part_addresses[4]),
	          std::vector<uint32_t>(101, 0xEE));
}
