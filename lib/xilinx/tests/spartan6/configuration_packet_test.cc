/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <functional>

#include <absl/meta/type_traits.h>
#include <gtest/gtest.h>
#include <prjxray/bit_ops.h>

#include <prjxray/xilinx/architectures.h>

using namespace prjxray::xilinx;

constexpr uint32_t kType1NOP = prjxray::bit_field_set<uint32_t>(0, 15, 13, 0x1);

const uint32_t MakeType1(const int opcode,
                         const int address,
                         const int word_count) {
	return prjxray::bit_field_set<uint32_t>(
	    prjxray::bit_field_set<uint32_t>(
	        prjxray::bit_field_set<uint32_t>(
	            prjxray::bit_field_set<uint32_t>(0x0, 15, 13, 0x1), 12, 11,
	            opcode),
	        10, 5, address),
	    4, 0, word_count);
}

const std::vector<uint32_t> MakeType2(const int opcode,
                                      const int address,
                                      const int word_count) {
	uint32_t header = prjxray::bit_field_set<uint32_t>(
	    prjxray::bit_field_set<uint32_t>(
	        prjxray::bit_field_set<uint32_t>(
	            prjxray::bit_field_set<uint32_t>(0x0, 15, 13, 0x2), 12, 11,
	            opcode),
	        10, 5, address),
	    4, 0, 0);
	uint32_t wcr1 = (word_count >> 16) & 0xFFFF;
	uint32_t wcr2 = (word_count & 0xFFFF);
	return std::vector<uint32_t>{header, wcr1, wcr2};
}

TEST(ConfigPacket, InitWithZeroBytes) {
	auto packet =
	    ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords({});

	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	EXPECT_FALSE(packet.second);
}

TEST(ConfigPacket, InitWithType1Nop) {
	std::vector<uint32_t> words{kType1NOP};
	absl::Span<uint32_t> word_span(words);
	auto packet = ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
	    word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(),
	          ConfigurationPacket<Spartan6::ConfRegType>::Opcode::NOP);
	EXPECT_EQ(packet.second->address(), Spartan6::ConfRegType::CRC);
	EXPECT_EQ(packet.second->data(), absl::Span<uint32_t>());
}

TEST(ConfigPacket, InitWithType1Read) {
	std::vector<uint32_t> words{MakeType1(0x1, 0x3, 2), 0xAA, 0xBB};
	absl::Span<uint32_t> word_span(words);
	auto packet = ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
	    word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(),
	          ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Read);
	EXPECT_EQ(packet.second->address(), Spartan6::ConfRegType::FDRI);
	EXPECT_EQ(packet.second->data(), word_span.subspan(1));
}

TEST(ConfigPacket, InitWithType1Write) {
	std::vector<uint32_t> words{MakeType1(0x2, 0x4, 2), 0xAA, 0xBB};
	absl::Span<uint32_t> word_span(words);
	auto packet = ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
	    word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(),
	          ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Write);
	EXPECT_EQ(packet.second->address(), Spartan6::ConfRegType::FDRO);
	EXPECT_EQ(packet.second->data(), word_span.subspan(1));
}

TEST(ConfigPacket, InitWithType2WithPreviousPacket) {
	std::vector<uint32_t> words{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
	std::vector<uint32_t> type2 = MakeType2(0x01, 0x03, 12);
	words.insert(words.begin(), type2.begin(), type2.end());
	absl::Span<uint32_t> word_span(words);
	auto packet = ConfigurationPacket<Spartan6::ConfRegType>::InitWithWords(
	    word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(),
	          ConfigurationPacket<Spartan6::ConfRegType>::Opcode::Read);
	EXPECT_EQ(packet.second->address(), Spartan6::ConfRegType::FDRI);
	EXPECT_EQ(packet.second->data(), word_span.subspan(3));
}
