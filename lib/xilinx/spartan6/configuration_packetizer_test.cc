#include <prjxray/xilinx/spartan6/configuration_packetizer.h>

#include <map>
#include <vector>

#include <gtest/gtest.h>

namespace spartan6 = prjxray::xilinx::spartan6;

TEST(ConfigurationPacketizerTest, EmptyConfigGeneratesNoPackets) {
	auto part = spartan6::Part::FromFile("configuration_test.yaml");
	ASSERT_TRUE(part);

	std::map<spartan6::FrameAddress, std::vector<uint32_t>> frames;
	spartan6::Configuration config(*part, &frames);
	spartan6::ConfigurationPacketizer packetizer(config);

	EXPECT_EQ(packetizer.begin(), packetizer.end());
}

TEST(ConfigurationPacketizerTest, ConfigWithFramesGeneratesPackets) {
	auto part = spartan6::Part::FromFile("configuration_test.yaml");
	ASSERT_TRUE(part);

	std::map<spartan6::FrameAddress, std::vector<uint32_t>> frames;
	frames[0] = std::vector<uint32_t>(101, 0xAA);
	frames[1] = std::vector<uint32_t>(101, 0xBB);

	spartan6::Configuration config(*part, &frames);

	EXPECT_EQ(config.frames().at(0), frames[0]);
	EXPECT_EQ(config.frames().at(1), frames[1]);

	spartan6::ConfigurationPacketizer packetizer(config);

	auto packet = packetizer.begin();
	ASSERT_NE(packet, packetizer.end());

	// Write 0x0 to FAR
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          spartan6::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), spartan6::ConfigurationRegister::FAR);
	EXPECT_EQ(packet->data(), std::vector<uint32_t>{0});

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          spartan6::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), spartan6::ConfigurationRegister::FDRI);
	EXPECT_EQ(packet->data(), frames[0]);

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          spartan6::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), spartan6::ConfigurationRegister::FAR);
	EXPECT_EQ(packet->data(), std::vector<uint32_t>{1});

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          spartan6::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), spartan6::ConfigurationRegister::FDRI);
	EXPECT_EQ(packet->data(), frames[1]);

	++packet;
	EXPECT_EQ(packet, packetizer.end());
}

TEST(ConfigurationPacketizerTest, ConfigWithFrameAtEndOfRowGeneratesZerofill) {
	auto part = spartan6::Part::FromFile("configuration_test.yaml");
	ASSERT_TRUE(part);

	spartan6::FrameAddress last_frame_in_first_row(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 43, 41);

	std::map<spartan6::FrameAddress, std::vector<uint32_t>> frames;
	frames[last_frame_in_first_row] = std::vector<uint32_t>(101, 0xAA);

	spartan6::Configuration config(*part, &frames);
	spartan6::ConfigurationPacketizer packetizer(config);

	auto packet = packetizer.begin();
	ASSERT_NE(packet, packetizer.end());

	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          spartan6::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), spartan6::ConfigurationRegister::FAR);
	EXPECT_EQ(packet->data(),
	          std::vector<uint32_t>{last_frame_in_first_row});

	++packet;
	ASSERT_NE(packet, packetizer.end());
	EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(1));
	EXPECT_EQ(packet->opcode(),
	          spartan6::ConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet->address(), spartan6::ConfigurationRegister::FDRI);
	EXPECT_EQ(packet->data(), frames[last_frame_in_first_row]);

	for (int ii = 0; ii < 202; ++ii) {
		++packet;
		ASSERT_NE(packet, packetizer.end());
		EXPECT_EQ(packet->header_type(), static_cast<unsigned int>(0));
		EXPECT_EQ(packet->opcode(),
		          spartan6::ConfigurationPacket::Opcode::NOP);
		EXPECT_EQ(packet->address(),
		          spartan6::ConfigurationRegister::CRC);
		EXPECT_EQ(packet->data(), std::vector<uint32_t>());
	}

	++packet;
	EXPECT_EQ(packet, packetizer.end());
}
