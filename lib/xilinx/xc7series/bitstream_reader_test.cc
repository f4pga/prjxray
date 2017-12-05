#include <array>

#include <gtest/gtest.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/configuration_packet.h>

using prjxray::xilinx::xc7series::BitstreamReader;
using prjxray::xilinx::xc7series::ConfigurationPacket;

TEST(BitstreamReaderTest, InitWithEmptyBytesReturnsNull) {
	absl::Span<uint8_t> bitstream;
	auto reader = BitstreamReader::InitWithBytes(bitstream);
	EXPECT_FALSE(reader);
}

TEST(BitstreamReaderTest, InitWithOnlySyncReturnsObject) {
	std::vector<uint8_t> bitstream{0xAA, 0x99, 0x55, 0x66};
	auto reader = BitstreamReader::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(BitstreamReaderTest,
     InitWithSyncAfterNonWordSizedPaddingReturnsObject) {
	std::vector<uint8_t> bitstream{
		0xFF, 0xFE,
		0xAA, 0x99, 0x55, 0x66
	};
	auto reader = BitstreamReader::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(BitstreamReaderTest,
     InitWithSyncAfterWordSizedPaddingReturnsObject) {
	std::vector<uint8_t> bitstream{
		0xFF, 0xFE, 0xFD, 0xFC,
		0xAA, 0x99, 0x55, 0x66
	};
	auto reader = BitstreamReader::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(BitstreamReaderTest, ParsesType1Packet) {
	std::vector<uint8_t> bitstream{
		0xAA, 0x99, 0x55, 0x66,  // sync
		0b001'00'000, 0b00000000, 0b000'00'000, 0b00000000,  // NOP
	};
	auto reader = BitstreamReader::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	ASSERT_NE(reader->begin(), reader->end());

	auto first_packet = reader->begin();
	EXPECT_EQ(first_packet->opcode(), ConfigurationPacket::Opcode::NOP);

	EXPECT_EQ(++first_packet, reader->end());
}

TEST(BitstreamReaderTest, ParseType2PacketWithoutType1Fails) {
	std::vector<uint8_t> bitstream{
		0xAA, 0x99, 0x55, 0x66,  // sync
		0b010'00'000, 0b00000000, 0b000'00'000, 0b00000000,  // NOP
	};
	auto reader = BitstreamReader::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	EXPECT_EQ(reader->begin(), reader->end());
}


TEST(BitstreamReaderTest, ParsesType2AfterType1Packet) {
	std::vector<uint8_t> bitstream{
		0xAA, 0x99, 0x55, 0x66,  // sync
		0b001'01'000, 0b00000000, 0b011'00'000, 0b00000000,  // Read
		0b010'01'000, 0b00000000, 0b0000000000, 0b00000100,
		0x1, 0x2, 0x3, 0x4,
		0x5, 0x6, 0x7, 0x8,
		0x9, 0xA, 0xB, 0xC,
		0xD, 0xE, 0xF, 0x10,
	};
	std::vector<uint32_t> data_words{
		0x01020304, 0x05060708, 0x090A0B0C, 0x0D0E0F10};

	auto reader = BitstreamReader::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	ASSERT_NE(reader->begin(), reader->end());

	auto first_packet = reader->begin();
	EXPECT_EQ(first_packet->opcode(), ConfigurationPacket::Opcode::Read);
	EXPECT_EQ(first_packet->address(), static_cast<uint32_t>(0x3));
	EXPECT_EQ(first_packet->data(), absl::Span<uint32_t>());

	auto second_packet = ++first_packet;
	ASSERT_NE(second_packet, reader->end());
	EXPECT_EQ(second_packet->opcode(), ConfigurationPacket::Opcode::Read);
	EXPECT_EQ(second_packet->address(), static_cast<uint32_t>(0x3));
	EXPECT_EQ(first_packet->data(), absl::Span<uint32_t>(data_words));

	EXPECT_EQ(++first_packet, reader->end());
}
