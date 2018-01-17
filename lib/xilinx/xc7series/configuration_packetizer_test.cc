#include <prjxray/xilinx/xc7series/configuration_packetizer.h>

#include <map>
#include <vector>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(ConfigurationPacketizerTest, EmptyConfigGeneratesNoPackets) {
	auto part = xc7series::Part::FromFile("configuration_test.yaml");
	ASSERT_TRUE(part);

	std::map<xc7series::FrameAddress, std::vector<uint32_t>> frames;
	xc7series::Configuration config(*part, &frames);
	xc7series::ConfigurationPacketizer packetizer(config);

	EXPECT_EQ(packetizer.begin(), packetizer.end());
}

TEST(ConfigurationPacketizerTest, ConfigWithFramesGeneratesPackets) {
	auto part = xc7series::Part::FromFile("configuration_test.yaml");
	ASSERT_TRUE(part);

	std::map<xc7series::FrameAddress, std::vector<uint32_t>> frames;
	frames[0] = std::vector<uint32_t>(101, 0xAA);
	frames[1] = std::vector<uint32_t>(101, 0xBB);

	xc7series::Configuration config(*part, &frames);

	EXPECT_EQ(config.frames().at(0), frames[0]);
	EXPECT_EQ(config.frames().at(1), frames[1]);

	xc7series::ConfigurationPacketizer packetizer(config);

	auto packet = packetizer.begin();
	ASSERT_NE(packet, packetizer.end());

	// Write 0x0 to FAR
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          xc7series::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), xc7series::ConfigurationRegister::FAR);
	EXPECT_EQ(packet->data(), std::vector<uint32_t>{0});

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          xc7series::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), xc7series::ConfigurationRegister::FDRI);
	EXPECT_EQ(packet->data(), frames[0]);

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          xc7series::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), xc7series::ConfigurationRegister::FAR);
	EXPECT_EQ(packet->data(), std::vector<uint32_t>{1});

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          xc7series::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), xc7series::ConfigurationRegister::FDRI);
	EXPECT_EQ(packet->data(), frames[1]);

	++packet;
	EXPECT_EQ(packet, packetizer.end());
}

TEST(ConfigurationPacketizerTest, ConfigWithFrameAtEndOfRowGeneratesZerofill) {
	auto part = xc7series::Part::FromFile("configuration_test.yaml");
	ASSERT_TRUE(part);

	xc7series::FrameAddress last_frame_in_first_row(
	    xc7series::BlockType::CLB_IO_CLK, false, 0, 43, 41);

	std::map<xc7series::FrameAddress, std::vector<uint32_t>> frames;
	frames[last_frame_in_first_row] = std::vector<uint32_t>(101, 0xAA);

	xc7series::Configuration config(*part, &frames);
	xc7series::ConfigurationPacketizer packetizer(config);

	auto packet = packetizer.begin();
	ASSERT_NE(packet, packetizer.end());

	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          xc7series::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), xc7series::ConfigurationRegister::FAR);
	EXPECT_EQ(packet->data(),
	          std::vector<uint32_t>{last_frame_in_first_row});

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          xc7series::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), xc7series::ConfigurationRegister::FDRI);
	EXPECT_EQ(packet->data(), frames[last_frame_in_first_row]);

	for (int ii = 0; ii < 202; ++ii) {
		++packet;
		ASSERT_NE(packet, packetizer.end());
		EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(0));
		EXPECT_EQ(packet->opcode(),
		          xc7series::ConfigurationPacket::Opcode::NOP);
		EXPECT_EQ(packet->address(),
		          xc7series::ConfigurationRegister::CRC);
		EXPECT_EQ(packet->data(), std::vector<uint32_t>());
	}

	++packet;
	EXPECT_EQ(packet, packetizer.end());
}
