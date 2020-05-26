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

#include <gtest/gtest.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_reader.h>
#include <prjxray/xilinx/bitstream_writer.h>

#include <prjxray/bit_ops.h>

using namespace prjxray::xilinx;

constexpr uint32_t kType1NOP = prjxray::bit_field_set<uint32_t>(0, 15, 13, 0x1);

extern const uint32_t MakeType1(const int opcode,
                                const int address,
                                const int word_count);

extern const std::vector<uint32_t> MakeType2(const int opcode,
                                             const int address,
                                             const int word_count);

void dump_packets(BitstreamWriter<Spartan6> writer, bool nl = true) {
	int i = 0;
	// for (uint32_t x : itr) {
	for (auto itr = writer.begin(); itr != writer.end(); ++itr) {
		if (nl) {
			printf("% 3d: 0x0%08X\n", i, *itr);
		} else {
			printf("0x0%08X, ", *itr);
		}
		fflush(stdout);
		++i;
	}
	if (!nl) {
		printf("\n");
	}
}

// Special all 0's
void AddType0(
    std::vector<std::unique_ptr<ConfigurationPacket<Spartan6::ConfRegType>>>&
        packets) {
	// InitWithWords doesn't like type 0
	/*
	static std::vector<uint32_t> words{0x00000000};
	absl::Span<uint32_t> word_span(words);
	auto packet =
	ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(word_span);
	packets.push_back(*(packet.second));
	*/
	static std::vector<uint32_t> words{};
	absl::Span<uint32_t> word_span(words);
	// CRC is config value 0
	packets.emplace_back(new ConfigurationPacket<Spartan6::ConfRegType>(
	    0, ConfigurationPacket<Spartan6::ConfRegType>::NOP,
	    Spartan6::ConfRegType::CRC, word_span));
}

void AddType1(
    std::vector<std::unique_ptr<ConfigurationPacket<Spartan6::ConfRegType>>>&
        packets) {
	static std::vector<uint32_t> words{MakeType1(0x2, 0x3, 2), 0xAA, 0xBB};
	absl::Span<uint32_t> word_span(words);
	auto packet = ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
	    word_span);
	packets.emplace_back(
	    new ConfigurationPacket<Spartan6::ConfRegType>(*(packet.second)));
}

// Empty
void AddType1E(
    std::vector<std::unique_ptr<ConfigurationPacket<Spartan6::ConfRegType>>>&
        packets) {
	static std::vector<uint32_t> words{MakeType1(0x2, 0x3, 0)};
	absl::Span<uint32_t> word_span(words);
	auto packet = ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
	    word_span);
	packets.emplace_back(
	    new ConfigurationPacket<Spartan6::ConfRegType>(*(packet.second)));
}

void AddType2(Spartan6::ConfigurationPackage& packets) {
	// Type 2 packet with data
	{
		static std::vector<uint32_t> words;
		words = MakeType2(0x02, 0x3, 12);
		std::vector<uint32_t> payload{1, 2, 3, 4,  5,  6,
		                              7, 8, 9, 10, 11, 12};
		words.insert(words.end(), payload.begin(), payload.end());
		std::cout << words.size();
		absl::Span<uint32_t> word_span(words);
		auto packet =
		    ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
		        word_span);
		packets.emplace_back(
		    new ConfigurationPacket<Spartan6::ConfRegType>(
		        *(packet.second)));
	}
}

// Empty packets should produce just the header
TEST(BitstreamWriterTest, WriteHeader) {
	std::vector<std::unique_ptr<ConfigurationPacket<Spartan6::ConfRegType>>>
	    packets;

	BitstreamWriter<Spartan6> writer(packets);
	std::vector<uint32_t> words(writer.begin(), writer.end());

	// Per UG380 pg 78: Bus Width Auto Detection
	std::vector<uint32_t> ref_header{0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
	                                 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
	                                 0xAA99, 0x5566};
	EXPECT_EQ(words, ref_header);

	// dump_packets(writer);
}

TEST(BitstreamWriterTest, WriteType0) {
	std::vector<std::unique_ptr<ConfigurationPacket<Spartan6::ConfRegType>>>
	    packets;
	AddType0(packets);
	BitstreamWriter<Spartan6> writer(packets);
	// dump_packets(writer, false);
	std::vector<uint32_t> words(writer.begin(), writer.end());
	std::vector<uint32_t> ref{0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
	                          0xFFFF, 0xFFFF, 0xFFFF, 0xAA99, 0x5566,
	                          // Type 0
	                          0x0000};
	EXPECT_EQ(words, ref);
}

TEST(BitstreamWriterTest, WriteType1) {
	Spartan6::ConfigurationPackage packets;
	AddType1(packets);
	BitstreamWriter<Spartan6> writer(packets);
	// dump_packets(writer, false);
	std::vector<uint32_t> words(writer.begin(), writer.end());
	std::vector<uint32_t> ref{// Bus width + sync
	                          0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
	                          0xFFFF, 0xFFFF, 0xFFFF, 0xAA99, 0x5566,
	                          // Type 1
	                          0x3062, 0x00AA, 0x00BB};
	EXPECT_EQ(words, ref);
}

TEST(BitstreamWriterTest, WriteType2) {
	Spartan6::ConfigurationPackage packets;
	AddType2(packets);
	BitstreamWriter<Spartan6> writer(packets);
	// dump_packets(writer, false);
	std::vector<uint32_t> words(writer.begin(), writer.end());
	std::vector<uint32_t> ref{
	    // Bus width + sync
	    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
	    0xAA99, 0x5566, 0x5060, 0x0001, 0x0002, 0x0003, 0x0004, 0x0005,
	    0x0006, 0x0007, 0x0008, 0x0009, 0x000A, 0x000B, 0x000C};
	EXPECT_EQ(words, ref);
}

TEST(BitstreamWriterTest, WriteMulti) {
	Spartan6::ConfigurationPackage packets;
	AddType1(packets);
	AddType1E(packets);
	AddType2(packets);
	AddType1E(packets);
	BitstreamWriter<Spartan6> writer(packets);
	// dump_packets(writer, false);
	std::vector<uint32_t> words(writer.begin(), writer.end());
	std::vector<uint32_t> ref{// Bus width + sync
	                          0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
	                          0xFFFF, 0xFFFF, 0xFFFF, 0xAA99, 0x5566,
	                          // Type1
	                          0x3062, 0x00AA, 0x00BB,
	                          // Type1
	                          0x3060,
	                          // Type 1 + type 2 header
	                          0x5060, 0x0001, 0x0002, 0x0003, 0x0004,
	                          0x0005, 0x0006, 0x0007, 0x0008, 0x0009,
	                          0x000A, 0x000B, 0x000C,
	                          // Type 1
	                          0x3060};
	EXPECT_EQ(words, ref);
}
