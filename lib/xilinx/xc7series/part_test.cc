#include <prjxray/xilinx/xc7series/part.h>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(PartTest, GetNextAddressWhereNextIsInValidRange) {
	std::vector<xc7series::ConfigurationFrameRange> ranges;
	ranges.push_back(xc7series::ConfigurationFrameRange(0x0, 0xF));
	ranges.push_back(xc7series::ConfigurationFrameRange(0x20, 0x2F));

	xc7series::Part part(0x1234, ranges);

	auto next_address = part.GetNextFrameAddress(0x4);
	EXPECT_TRUE(next_address);
	EXPECT_EQ(static_cast<uint32_t>(0x5), *next_address);
}

TEST(PartTest, GetNextAddressWhereNextIsBetweenRanges) {
	std::vector<xc7series::ConfigurationFrameRange> ranges;
	ranges.push_back(xc7series::ConfigurationFrameRange(0x0, 0xF));
	ranges.push_back(xc7series::ConfigurationFrameRange(0x20, 0x2F));

	xc7series::Part part(0x1234, ranges);

	auto next_address = part.GetNextFrameAddress(0xF);
	EXPECT_TRUE(next_address);
	EXPECT_EQ(static_cast<uint32_t>(0x20), *next_address);
}

TEST(PartTest, GetNextAddressWhereNextWouldBePastLastRange) {
	std::vector<xc7series::ConfigurationFrameRange> ranges;
	ranges.push_back(xc7series::ConfigurationFrameRange(0x0, 0xF));
	ranges.push_back(xc7series::ConfigurationFrameRange(0x20, 0x2F));

	xc7series::Part part(0x1234, ranges);

	auto next_address = part.GetNextFrameAddress(0x2F);
	EXPECT_FALSE(next_address);
}
