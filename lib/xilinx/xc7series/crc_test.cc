#include <prjxray/xilinx/xc7series/crc.h>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(IcapCrcTest, SimpleTests) {
	// CRC for Zero Data
	EXPECT_EQ(xc7series::icap_crc(0, 0, 0), 0x0L);
	// Polynomial (single bit operation)
	EXPECT_EQ(xc7series::icap_crc(1 << 4, 0, 0), 0x82F63B78);
	// All Reg/Data bits
	EXPECT_EQ(xc7series::icap_crc(~0, ~0, 0), 0xBF86D4DF);
	// All CRC bits
	EXPECT_EQ(xc7series::icap_crc(0, 0, ~0), 0xC631E365);
}
