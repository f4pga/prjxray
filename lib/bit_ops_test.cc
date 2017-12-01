#include <prjxray/bit_ops.h>

#include <gtest/gtest.h>

TEST(BitMaskTest, Bit0) {
	uint32_t expected = prjxray::bit_mask<uint32_t>(0);
	EXPECT_EQ(static_cast<uint32_t>(0x1), expected);
}

TEST(BitMaskTest, Bit3) {
	uint32_t expected = prjxray::bit_mask<uint32_t>(3);
	EXPECT_EQ(static_cast<uint32_t>(0x8), expected);
}

TEST(BitMaskRange, SingleBit) {
	uint32_t expected = prjxray::bit_mask_range<uint32_t>(23, 23);
	EXPECT_EQ(static_cast<uint32_t>(0x800000), expected);
}

TEST(BitMaskRange, DownToZero) {
	uint32_t expected = prjxray::bit_mask_range<uint32_t>(7, 0);
	EXPECT_EQ(static_cast<uint32_t>(0xFF), expected);
}

TEST(BitMaskRange, MiddleBits) {
	uint32_t expected = prjxray::bit_mask_range<uint32_t>(18, 8);
	EXPECT_EQ(static_cast<uint32_t>(0x7FF00), expected);
}

TEST(BitFieldGetTest, OneSelectedBit) {
	uint32_t expected = prjxray::bit_field_get(0xFFFFFFFF, 23, 23);
	EXPECT_EQ(static_cast<uint32_t>(1), expected);
}

TEST(BitFieldGetTest, SelectDownToZero) {
	uint32_t expected = prjxray::bit_field_get(0xFFCCBBAA, 7, 0);
	EXPECT_EQ(static_cast<uint32_t>(0xAA), expected);
}

TEST(BitFieldGetTest, SelectMidway) {
	uint32_t expected = prjxray::bit_field_get(0xFFCCBBAA, 18, 8);
	EXPECT_EQ(static_cast<uint32_t>(0x4BB), expected);
}
