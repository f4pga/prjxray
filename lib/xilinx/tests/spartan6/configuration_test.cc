/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <cstdint>
#include <iostream>
#include <vector>

#include <absl/types/span.h>
#include <gtest/gtest.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/configuration.h>
#include <prjxray/xilinx/spartan6/frame_address.h>
#include <yaml-cpp/yaml.h>

using namespace prjxray::xilinx;

TEST(ConfigurationTest, ConstructFromPacketsWithSingleFrame) {
	std::vector<spartan6::FrameAddress> test_part_addresses;
	test_part_addresses.push_back(0x0A);
	test_part_addresses.push_back(0x0B);

	spartan6::Part test_part(0x1234, test_part_addresses);

	std::vector<uint32_t> idcode{0x1234};
	std::vector<uint32_t> cmd{0x0001};
	std::vector<uint32_t> frame_address{0x345};
	std::vector<uint32_t> frame(65, 0xAA);

	std::vector<ConfigurationPacket<typename Spartan6::ConfRegType>>
	    packets{
	        {
	            static_cast<unsigned int>(0x1),
	            ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	            Spartan6::ConfRegType::IDCODE,
	            absl::MakeSpan(idcode),
	        },
	        {
	            static_cast<unsigned int>(0x1),
	            ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	            Spartan6::ConfRegType::FAR_MIN,
	            absl::MakeSpan(frame_address),
	        },
	        {
	            static_cast<unsigned int>(0x1),
	            ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	            Spartan6::ConfRegType::CMD,
	            absl::MakeSpan(cmd),
	        },
	        {
	            static_cast<unsigned int>(0x1),
	            ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	            Spartan6::ConfRegType::FDRI,
	            absl::MakeSpan(frame),
	        },
	    };

	auto test_config =
	    Configuration<Spartan6>::InitWithPackets(test_part, packets);
	ASSERT_TRUE(test_config);

	EXPECT_EQ(test_config->part().idcode(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(test_config->frames().size(), static_cast<size_t>(1));
	EXPECT_EQ(test_config->frames().at(0x345), frame);
}

TEST(ConfigurationTest, ConstructFromPacketsWithAutoincrement) {
	std::vector<spartan6::FrameAddress> test_part_addresses;
	for (int ii = 0x310; ii < 0x320; ++ii) {
		test_part_addresses.push_back(ii);
	}

	for (int ii = 0x330; ii < 0x331; ++ii) {
		test_part_addresses.push_back(ii);
	}

	spartan6::Part test_part(0x1234, test_part_addresses);

	std::vector<uint32_t> idcode{0x1234};
	std::vector<uint32_t> cmd{0x0001};
	std::vector<uint32_t> frame_address{0x31f};
	std::vector<uint32_t> frame(65 * 2, 0xAA);
	std::fill_n(frame.begin() + 65, 65, 0xBB);

	std::vector<ConfigurationPacket<Spartan6::ConfRegType>> packets{
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::IDCODE,
	        absl::MakeSpan(idcode),
	    },
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::FAR_MIN,
	        absl::MakeSpan(frame_address),
	    },
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::CMD,
	        absl::MakeSpan(cmd),
	    },
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::FDRI,
	        absl::MakeSpan(frame),
	    },
	};

	auto test_config =
	    Configuration<Spartan6>::InitWithPackets(test_part, packets);
	ASSERT_TRUE(test_config);

	absl::Span<uint32_t> frame_span(frame);
	EXPECT_EQ(test_config->part().idcode(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(test_config->frames().size(), static_cast<size_t>(2));
	EXPECT_EQ(test_config->frames().at(0x31f),
	          std::vector<uint32_t>(65, 0xAA));
	// TODO This test fails with a C++ exception because the address
	// of next frame is 0x320 instead of 0x330 as defined in the test_part
	// EXPECT_EQ(test_config->frames().at(0x330),
	//          std::vector<uint32_t>(65, 0xBB));
}

TEST(ConfigurationTest, DISABLED_CheckForPaddingAfterIOBFrame) {
	std::vector<spartan6::FrameAddress> test_part_addresses = {
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0),
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 1, 0, 0),
	    spartan6::FrameAddress(spartan6::BlockType::IOB, 2, 0, 0)};

	auto test_part = absl::optional<spartan6::Part>(
	    spartan6::Part(0x1234, test_part_addresses));

	Frames<Spartan6> frames;
	frames.getFrames().emplace(std::make_pair(
	    test_part_addresses.at(0), std::vector<uint32_t>(65, 0xAA)));
	frames.getFrames().emplace(std::make_pair(
	    test_part_addresses.at(1), std::vector<uint32_t>(65, 0xBB)));
	frames.getFrames().emplace(std::make_pair(
	    test_part_addresses.at(2), std::vector<uint32_t>(65, 0xCC)));
	ASSERT_EQ(frames.getFrames().size(), 3);

	Configuration<Spartan6>::PacketData packet_data =
	    Configuration<Spartan6>::createType2ConfigurationPacketData(
	        frames.getFrames(), test_part);
	// createType2ConfigurationPacketData should add a 16-bit pad word after
	// after the IOB frame
	EXPECT_EQ(packet_data.size(), 3 * 65 + 1);

	std::vector<uint32_t> idcode{0x1234};
	std::vector<uint32_t> cmd{0x0001};
	std::vector<uint32_t> frame_address{0x0};

	std::vector<ConfigurationPacket<Spartan6::ConfRegType>> packets{
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::IDCODE,
	        absl::MakeSpan(idcode),
	    },
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::FAR,
	        absl::MakeSpan(frame_address),
	    },
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::CMD,
	        absl::MakeSpan(cmd),
	    },
	    {
	        static_cast<unsigned int>(0x1),
	        ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write,
	        Spartan6::ConfRegType::FDRI,
	        absl::MakeSpan(packet_data),
	    },
	};

	auto test_config =
	    Configuration<Spartan6>::InitWithPackets(*test_part, packets);
	ASSERT_EQ(test_config->frames().size(), 5);
	for (auto& frame : test_config->frames()) {
		EXPECT_EQ(frame.second, frames.getFrames().at(frame.first));
	}
}
