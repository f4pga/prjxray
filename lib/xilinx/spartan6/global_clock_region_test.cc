#include <prjxray/xilinx/spartan6/global_clock_region.h>

#include <gtest/gtest.h>

namespace spartan6 = prjxray::xilinx::spartan6;

TEST(GlobalClockRegionTest, IsValidFrameAddress) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 2));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 1));

	spartan6::GlobalClockRegion global_clock_region(addresses.begin(),
	                                                addresses.end());

	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 0)));
	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 0)));
	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::BLOCK_RAM, false, 0, 0, 2)));
	EXPECT_TRUE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 0)));

	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 2)));
	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 2, 0)));
	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 2, 0, 0)));
	EXPECT_FALSE(
	    global_clock_region.IsValidFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CFG_CLB, false, 0, 0, 2)));
}

TEST(GlobalClockRegionTest,
     GetNextFrameAddressYieldNextAddressInGlobalClockRegion) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 2));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 1));

	spartan6::GlobalClockRegion global_clock_region(addresses.begin(),
	                                                addresses.end());

	auto next_address =
	    global_clock_region.GetNextFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          spartan6::FrameAddress(spartan6::BlockType::CLB_IO_CLK, false,
	                                 0, 0, 1));

	next_address =
	    global_clock_region.GetNextFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          spartan6::FrameAddress(spartan6::BlockType::CLB_IO_CLK, false,
	                                 0, 1, 0));

	next_address =
	    global_clock_region.GetNextFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          spartan6::FrameAddress(spartan6::BlockType::CLB_IO_CLK, false,
	                                 1, 0, 0));

	next_address =
	    global_clock_region.GetNextFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::BLOCK_RAM, false, 0, 0, 1));
	ASSERT_TRUE(next_address);
	EXPECT_EQ(*next_address,
	          spartan6::FrameAddress(spartan6::BlockType::BLOCK_RAM, false,
	                                 0, 0, 2));
}

TEST(GlobalClockRegionTest,
     GetNextFrameAddressYieldNothingAtEndOfGlobalClockRegion) {
	std::vector<spartan6::FrameAddress> addresses;
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 0, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 0, 1, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 1));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::BLOCK_RAM, false, 0, 0, 2));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 0));
	addresses.push_back(spartan6::FrameAddress(
	    spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 1));

	spartan6::GlobalClockRegion global_clock_region(addresses.begin(),
	                                                addresses.end());

	EXPECT_FALSE(
	    global_clock_region.GetNextFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::CLB_IO_CLK, false, 1, 0, 1)));
	EXPECT_FALSE(
	    global_clock_region.GetNextFrameAddress(spartan6::FrameAddress(
	        spartan6::BlockType::BLOCK_RAM, false, 0, 0, 2)));
}
