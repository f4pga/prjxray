/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <array>

#include <absl/types/span.h>
#include <gtest/gtest.h>
#include <prjxray/xilinx/bitstream_reader.h>
#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/configuration_register.h>

#include <prjxray/big_endian_span.h>

using namespace prjxray::xilinx;
TEST(BitstreamReaderTest, InitWithEmptyBytesReturnsNull) {
	absl::Span<uint8_t> bitstream;
	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	EXPECT_FALSE(reader);
}

TEST(BitstreamReaderTest, InitWithOnlySyncReturnsObject) {
	std::vector<uint8_t> bitstream{0xAA, 0x99, 0x55, 0x66};
	absl::Span<std::vector<uint8_t>::value_type> bitstream_span(bitstream);
	// auto config_packets =
	//    bitstream_span.subspan(bitstream.end() - bitstream.begin());
	// auto big_endian_reader =
	// prjxray::make_big_endian_span<uint16_t>(bitstream_span);
	// std::vector<uint16_t> words{big_endian_reader.begin(),
	//                            big_endian_reader.end()};

	// for (auto word: words) {
	//   std::cout << "0x" << std::hex << word << std::endl;
	//}
	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(BitstreamReaderTest, InitWithSyncAfterNonWordSizedPaddingReturnsObject) {
	std::vector<uint8_t> bitstream{0xFF, 0xFE, 0xAA, 0x99, 0x55, 0x66};
	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(BitstreamReaderTest, InitWithSyncAfterWordSizedPaddingReturnsObject) {
	std::vector<uint8_t> bitstream{0xFF, 0xFE, 0xFD, 0xFC,
	                               0xAA, 0x99, 0x55, 0x66};
	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	EXPECT_TRUE(reader);
}

TEST(BitstreamReaderTest, ParsesType1Packet) {
	std::vector<uint8_t> bitstream{
	    0xAA, 0x99, 0x55, 0x66,  // sync
	    0x20, 0x00, 0x20, 0x00,  // NOP
	};
	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	ASSERT_NE(reader->begin(), reader->end());

	auto first_packet = reader->begin();
	EXPECT_EQ(first_packet->opcode(),
	          ConfigurationPacket<Spartan6>::Opcode::NOP);

	auto second_packet = ++first_packet;
	EXPECT_EQ(second_packet->opcode(),
	          ConfigurationPacket<Spartan6>::Opcode::NOP);

	EXPECT_EQ(++second_packet, reader->end());
}

TEST(BitstreamReaderTest, ParseType2PacketWithoutType1Fails) {
	std::vector<uint8_t> bitstream{
	    0xAA, 0x99, 0x55, 0x66,  // sync
	    0x40, 0x00, 0x40, 0x00,  // Type 2 NOP
	};
	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	EXPECT_EQ(reader->begin(), reader->end());
}

TEST(BitstreamReaderTest, ParsesType2AfterType1Packet) {
	std::vector<uint8_t> bitstream{
	    0xAA, 0x99,  // sync
	    0x55, 0x66,  // sync
	    0x28, 0x80,  // Type 1 Read zero bytes from FDRO
	    0x50, 0x60,  // Type 2 Write of 8 16-bit words
	    0x00, 0x00,  // WC1 bits 31:16
	    0x00, 0x08,  // WC2 bits 15:0
	    0x1,  0x2,  0x3, 0x4, 0x5, 0x6, 0x7, 0x8,
	    0x9,  0xA,  0xB, 0xC, 0xD, 0xE, 0xF, 0x10,
	};
	std::vector<uint32_t> data_words{0x0102, 0x0304, 0x0506, 0x0708,
	                                 0x090A, 0x0B0C, 0x0D0E, 0x0F10};

	auto reader = BitstreamReader<Spartan6>::InitWithBytes(bitstream);
	ASSERT_TRUE(reader);
	ASSERT_NE(reader->begin(), reader->end());

	auto first_packet = reader->begin();
	EXPECT_EQ(first_packet->opcode(),
	          ConfigurationPacket<Spartan6>::Opcode::Read);
	EXPECT_EQ(first_packet->address(), Spartan6::ConfRegType::FDRO);
	EXPECT_EQ(first_packet->data(), absl::Span<uint32_t>());

	auto third_packet = ++first_packet;
	ASSERT_NE(third_packet, reader->end());
	EXPECT_EQ(third_packet->opcode(),
	          ConfigurationPacket<Spartan6>::Opcode::Write);
	EXPECT_EQ(third_packet->address(), Spartan6::ConfRegType::FDRI);
	(third_packet->data(), absl::Span<uint32_t>(data_words));
	EXPECT_EQ(++first_packet, reader->end());
}
