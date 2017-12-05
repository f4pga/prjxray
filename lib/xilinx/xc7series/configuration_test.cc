#include <prjxray/xilinx/xc7series/configuration.h>

#include <cstdint>
#include <vector>

#include <absl/types/span.h>
#include <gtest/gtest.h>
#include <prjxray/xilinx/xc7series/configuration_packet.h>
#include <prjxray/xilinx/xc7series/configuration_register.h>
#include <prjxray/xilinx/xc7series/part.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(ConfigurationTest, ConstructFromPacketsWithSingleFrame) {
	std::vector<xc7series::ConfigurationFrameRange> test_part_ranges;
	test_part_ranges.push_back(
			xc7series::ConfigurationFrameRange(0x4567, 0x4568));

	xc7series::Part test_part(0x1234, test_part_ranges);

	std::vector<uint32_t> idcode{0x1234};
	std::vector<uint32_t> cmd{0x0001};
	std::vector<uint32_t> frame_address{0x4567};
	std::vector<uint32_t> frame(101, 0xAA);

	std::vector<xc7series::ConfigurationPacket> packets{
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::IDCODE,
			absl::MakeSpan(idcode),
		},
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::FAR,
			absl::MakeSpan(frame_address),
		},
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::CMD,
			absl::MakeSpan(cmd),
		},
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::FDRI,
			absl::MakeSpan(frame),
		},
	};

	auto test_config = xc7series::Configuration::InitWithPackets(test_part, packets);
	ASSERT_TRUE(test_config);

	EXPECT_EQ(test_config->part().idcode(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(test_config->frames().size(), static_cast<size_t>(1));
	EXPECT_EQ(test_config->frames().at(0x4567), frame);
}

TEST(ConfigurationTest, ConstructFromPacketsWithAutoincrement) {
	std::vector<xc7series::ConfigurationFrameRange> test_part_ranges;
	test_part_ranges.push_back(
			xc7series::ConfigurationFrameRange(0x4560, 0x4570));
	test_part_ranges.push_back(
			xc7series::ConfigurationFrameRange(0x4580, 0x4590));

	xc7series::Part test_part(0x1234, test_part_ranges);

	std::vector<uint32_t> idcode{0x1234};
	std::vector<uint32_t> cmd{0x0001};
	std::vector<uint32_t> frame_address{0x456F};
	std::vector<uint32_t> frame(202, 0xAA);
	std::fill_n(frame.begin() + 101, 101, 0xBB);

	std::vector<xc7series::ConfigurationPacket> packets{
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::IDCODE,
			absl::MakeSpan(idcode),
		},
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::FAR,
			absl::MakeSpan(frame_address),
		},
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::CMD,
			absl::MakeSpan(cmd),
		},
		{
			static_cast<unsigned int>(0x1),
			xc7series::ConfigurationPacket::Opcode::Write,
			xc7series::ConfigurationRegister::FDRI,
			absl::MakeSpan(frame),
		},
	};

	auto test_config = xc7series::Configuration::InitWithPackets(test_part, packets);
	ASSERT_TRUE(test_config);

	absl::Span<uint32_t> frame_span(frame);
	EXPECT_EQ(test_config->part().idcode(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(test_config->frames().size(), static_cast<size_t>(2));
	EXPECT_EQ(test_config->frames().at(0x456F), frame_span.subspan(0, 101));
	EXPECT_EQ(test_config->frames().at(0x4580), frame_span.subspan(101));
}
