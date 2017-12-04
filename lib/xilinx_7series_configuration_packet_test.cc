#include <prjxray/xilinx_7series_configuration_packet.h>

#include <functional>

#include <absl/meta/type_traits.h>
#include <gtest/gtest.h>
#include <prjxray/bit_ops.h>

constexpr uint32_t kType1NOP = prjxray::bit_field_set<uint32_t>(0, 31, 29, 0x1);

constexpr uint32_t MakeType1(const int opcode, const int address, const int word_count) {
	return prjxray::bit_field_set<uint32_t>(
			prjxray::bit_field_set<uint32_t>(
				prjxray::bit_field_set<uint32_t>(
						prjxray::bit_field_set<uint32_t>(0x0, 31, 29, 0x1),
						28, 27, opcode),
				26, 13, address),
			10, 0, word_count);
}

constexpr uint32_t MakeType2(const int opcode, const int word_count) {
	return prjxray::bit_field_set<uint32_t>(
			prjxray::bit_field_set<uint32_t>(
					prjxray::bit_field_set<uint32_t>(0x0, 31, 29, 0x2),
					28, 27, opcode),
			26, 0, word_count);
}


TEST(ConfigPacket, InitWithZeroBytes) {
	auto packet = prjxray::Xilinx7SeriesConfigurationPacket::InitWithWords({});

	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	EXPECT_FALSE(packet.second);
}

TEST(ConfigPacket, InitWithType1Nop) {
	std::vector<uint32_t> words{kType1NOP};
	absl::Span<uint32_t> word_span(words);
	auto packet = prjxray::Xilinx7SeriesConfigurationPacket::InitWithWords(word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(), prjxray::Xilinx7SeriesConfigurationPacket::Opcode::NOP);
	EXPECT_EQ(packet.second->address(), static_cast<uint32_t>(0));
	EXPECT_EQ(packet.second->data(), absl::Span<uint32_t>());
}

TEST(ConfigPacket, InitWithType1Read) {
	std::vector<uint32_t> words{MakeType1(0x1, 0x1234, 2), 0xAA, 0xBB};
	absl::Span<uint32_t> word_span(words);
	auto packet = prjxray::Xilinx7SeriesConfigurationPacket::InitWithWords(word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(), prjxray::Xilinx7SeriesConfigurationPacket::Opcode::Read);
	EXPECT_EQ(packet.second->address(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(packet.second->data(), word_span.subspan(1));
}

TEST(ConfigPacket, InitWithType1Write) {
	std::vector<uint32_t> words{MakeType1(0x2, 0x1234, 2), 0xAA, 0xBB};
	absl::Span<uint32_t> word_span(words);
	auto packet = prjxray::Xilinx7SeriesConfigurationPacket::InitWithWords(word_span);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(), prjxray::Xilinx7SeriesConfigurationPacket::Opcode::Write);
	EXPECT_EQ(packet.second->address(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(packet.second->data(), word_span.subspan(1));
}

TEST(ConfigPacket, InitWithType2WithoutPreviousPacketFails) {
	std::vector<uint32_t> words{MakeType2(0x01, 12)};
	absl::Span<uint32_t> word_span(words);
	auto packet = prjxray::Xilinx7SeriesConfigurationPacket::InitWithWords(word_span);
	EXPECT_EQ(packet.first, words);
	EXPECT_FALSE(packet.second);
}

TEST(ConfigPacket, InitWithType2WithPreviousPacket) {
	prjxray::Xilinx7SeriesConfigurationPacket previous_packet(
			prjxray::Xilinx7SeriesConfigurationPacket::Read,
			0x1234, absl::Span<uint32_t>());
	std::vector<uint32_t> words{MakeType2(0x01, 12), 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
	absl::Span<uint32_t> word_span(words);
	auto packet = prjxray::Xilinx7SeriesConfigurationPacket::InitWithWords(
			word_span, &previous_packet);
	EXPECT_EQ(packet.first, absl::Span<uint32_t>());
	ASSERT_TRUE(packet.second);
	EXPECT_EQ(packet.second->opcode(), prjxray::Xilinx7SeriesConfigurationPacket::Opcode::Read);
	EXPECT_EQ(packet.second->address(), static_cast<uint32_t>(0x1234));
	EXPECT_EQ(packet.second->data(), word_span.subspan(1));
}
