/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CRC_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CRC_H_

#include <cstdint>

constexpr uint32_t kCrc32CastagnoliPolynomial = 0x82F63B78;

namespace prjxray {
namespace xilinx {
namespace xc7series {

// The CRC is calculated from each written data word and the current
// register address the data is written to.

// Extend the current CRC value with one register address (5bit) and
// frame data (32bit) pair and return the newly computed CRC value.

uint32_t icap_crc(uint32_t addr, uint32_t data, uint32_t prev) {
	constexpr int kAddressBitWidth = 5;
	constexpr int kDataBitWidth = 32;

	uint64_t poly = static_cast<uint64_t>(kCrc32CastagnoliPolynomial) << 1;
	uint64_t val = (static_cast<uint64_t>(addr) << 32) | data;
	uint64_t crc = prev;

	for (int i = 0; i < kAddressBitWidth + kDataBitWidth; i++) {
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
