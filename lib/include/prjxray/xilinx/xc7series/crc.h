#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CRC_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CRC_H_

#include <cstdint>

namespace prjxray {
namespace xilinx {
namespace xc7series {

// Extend the current CRC value with one address (5bit) and data (32bit) 
// pair and return the newly computed CRC value

uint32_t icap_crc(uint32_t addr, uint32_t data, uint32_t prev) {
	uint64_t val = ((uint64_t)addr << 32) | data;
	uint64_t crc = prev;
	uint64_t poly = 0x82F63B78L << 1;	// CRC-32C (Castagnoli)

	for (int i = 0; i < 37; i++) {
		if ((val & 1) != (crc & 1))
			crc ^= poly;

		val >>= 1;
		crc >>= 1;
	}
	return crc;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CRC_H_
