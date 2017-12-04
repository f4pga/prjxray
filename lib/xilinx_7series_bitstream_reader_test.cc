#include <array>

#include <gtest/gtest.h>
#include <prjxray/xilinx_7series_bitstream_reader.h>
#include <prjxray/xilinx_7series_configuration_packet.h>

using prjxray::Xilinx7SeriesBitstreamReader;
using prjxray::Xilinx7SeriesConfigurationPacket;

TEST(Xilinx7SeriesBitstreamReaderTest, InitWithEmptyBytesReturnsNull) {
	absl::Span<uint8_t> bitstream;
	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	EXPECT_FALSE(reader);
}

TEST(Xilinx7SeriesBitstreamReaderTest, InitWithOnlySyncReturnsObject) {
	std::vector<uint8_t> bitstream{0xAA, 0x99, 0x55, 0x66};
	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(Xilinx7SeriesBitstreamReaderTest,
     InitWithSyncAfterNonWordSizedPaddingReturnsObject) {
	std::vector<uint8_t> bitstream{
		0xFF, 0xFE,
		0xAA, 0x99, 0x55, 0x66
	};
	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(Xilinx7SeriesBitstreamReaderTest,
     InitWithSyncAfterWordSizedPaddingReturnsObject) {
	std::vector<uint8_t> bitstream{
		0xFF, 0xFE, 0xFD, 0xFC,
		0xAA, 0x99, 0x55, 0x66
	};
	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(Xilinx7SeriesBitstreamReaderTest, ParsesType1Packet) {
	std::vector<uint8_t> bitstream{
		0xAA, 0x99, 0x55, 0x66,  // sync
		0b001'00'000, 0b00000000, 0b000'00'000, 0b00000000,  // NOP
	};
	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	ASSERT_NE(reader->begin(), reader->end());

	auto first_packet = reader->begin();
	EXPECT_EQ(first_packet->opcode(), Xilinx7SeriesConfigurationPacket::Opcode::NOP);

	EXPECT_EQ(++first_packet, reader->end());
}

TEST(Xilinx7SeriesBitstreamReaderTest, ParseType2PacketWithoutType1Fails) {
	std::vector<uint8_t> bitstream{
		0xAA, 0x99, 0x55, 0x66,  // sync
		0b010'00'000, 0b00000000, 0b000'00'000, 0b00000000,  // NOP
	};
	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	EXPECT_EQ(reader->begin(), reader->end());
}


TEST(Xilinx7SeriesBitstreamReaderTest, ParsesType2AfterType1Packet) {
	std::vector<uint8_t> bitstream{
		0xAA, 0x99, 0x55, 0x66,  // sync
		0b001'01'000, 0b00000000, 0b011'00'000, 0b00000000,  // Read
		0b010'01'000, 0b00000000, 0b0000000000, 0b00000100,
		0x1, 0x2, 0x3, 0x4,
		0x5, 0x6, 0x7, 0x8,
		0x9, 0xA, 0xB, 0xC,
		0xD, 0xE, 0xF, 0x10,
	};
	std::vector<uint32_t> data_words{ 0x01020304, 0x05060708, 0x090A0B0C, 0x0D0E0F10};

	auto reader = Xilinx7SeriesBitstreamReader::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	ASSERT_NE(reader->begin(), reader->end());

	auto first_packet = reader->begin();
	EXPECT_EQ(first_packet->opcode(), Xilinx7SeriesConfigurationPacket::Opcode::Read);
	EXPECT_EQ(first_packet->address(), static_cast<uint32_t>(0x3));
	EXPECT_EQ(first_packet->data(), absl::Span<uint32_t>());

	auto second_packet = ++first_packet;
	ASSERT_NE(second_packet, reader->end());
	EXPECT_EQ(second_packet->opcode(), Xilinx7SeriesConfigurationPacket::Opcode::Read);
	EXPECT_EQ(second_packet->address(), static_cast<uint32_t>(0x3));
	EXPECT_EQ(first_packet->data(), absl::Span<uint32_t>(data_words));

	EXPECT_EQ(++first_packet, reader->end());
}
