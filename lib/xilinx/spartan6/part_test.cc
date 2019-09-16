#include <prjxray/xilinx/spartan6/part.h>

#include <gtest/gtest.h>

namespace spartan6 = prjxray::xilinx::spartan6;

TEST(PartTest, IsValidFrameAddress) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));

	spartan6::Part part(0x1234, addresses.begin(), addresses.end());

	EXPECT_TRUE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0)));
	EXPECT_TRUE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0)));
	EXPECT_TRUE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2)));
	EXPECT_TRUE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 0)));
	EXPECT_TRUE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0)));

	EXPECT_FALSE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 2)));
	EXPECT_FALSE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 2, 0)));
	EXPECT_FALSE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 2, 0, 0)));
	EXPECT_FALSE(part.IsValidFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::IOB, 0, 0, 2)));
}

TEST(PartTest, GetNextFrameAddressYieldNextAddressInPart) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));

	spartan6::Part part(0x1234, addresses.begin(), addresses.end());

	auto next_address = part.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(
	    *next_address,
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));

	next_address = part.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(
	    *next_address,
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));

	next_address = part.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(
	    *next_address,
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 0));

	next_address = part.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address, spartan6::FrameAddress(
	                             spartan6::BlockType::BLOCK_RAM, 0, 0, 0));

	next_address = part.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(
	    *next_address,
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
}

TEST(PartTest, GetNextFrameAddressYieldNothingAtEndOfPart) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 1, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 1, 0, 1));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 0));
	addresses.push_back(
	    spartan6::FrameAddress(spartan6::BlockType::CLB_IOI_CLK, 0, 0, 1));

	spartan6::Part part(0x1234, addresses.begin(), addresses.end());

	EXPECT_FALSE(part.GetNextFrameAddress(
	    spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 2)));
}
