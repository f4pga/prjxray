#include <prjxray/xilinx/xc7series/ecc.h>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(IcapEccTest, SimpleTests) {
	EXPECT_EQ(xc7series::icap_ecc(0, 0, 0), (uint32_t)0x0);
	EXPECT_EQ(xc7series::icap_ecc(0, 1, 0), (uint32_t)0x1320);
	EXPECT_EQ(xc7series::icap_ecc(0x7, 1, 0), (uint32_t)0x1420);
	EXPECT_EQ(xc7series::icap_ecc(0x26, 1, 0), (uint32_t)0x1820);
	EXPECT_EQ(xc7series::icap_ecc(0x32, ~0, 0), (uint32_t)0x000019AC);
	EXPECT_EQ(xc7series::icap_ecc(0x64, 0, 1), (uint32_t)0x00001001);
}

