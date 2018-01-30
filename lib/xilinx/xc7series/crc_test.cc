#include <prjxray/xilinx/xc7series/crc.h>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(IcapCrcTest, SimpleTests) {
	EXPECT_EQ(xc7series::icap_crc(0, 0, 0), (uint32_t)0x0);
	EXPECT_EQ(xc7series::icap_crc(~0, ~0, 0), 0xBF86D4DF);
	EXPECT_EQ(xc7series::icap_crc(0, 0, ~0), 0xC631E365);
	EXPECT_EQ(xc7series::icap_crc(1 << 4, 0, 0), 0x82F63B78);
}

