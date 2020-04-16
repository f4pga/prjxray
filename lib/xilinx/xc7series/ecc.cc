/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/ecc.h>
#include <cassert>
#include <cstdio>

namespace prjxray {
namespace xilinx {
namespace xc7series {

constexpr size_t kECCFrameNumber = 0x32;

uint32_t icap_ecc(uint32_t idx, uint32_t data, uint32_t ecc) {
	uint32_t val = idx * 32;  // bit offset

	if (idx > 0x25)  // avoid 0x800
		val += 0x1360;
	else if (idx > 0x6)  // avoid 0x400
		val += 0x1340;
	else  // avoid lower
		val += 0x1320;

	if (idx == 0x32)  // mask ECC
		data &= 0xFFFFE000;

	for (int i = 0; i < 32; i++) {
		if (data & 1)
			ecc ^= val + i;

		data >>= 1;
	}

	if (idx == 0x64) {  // last index
		uint32_t v = ecc & 0xFFF;
		v ^= v >> 8;
		v ^= v >> 4;
		v ^= v >> 2;
		v ^= v >> 1;
		ecc ^= (v & 1) << 12;  // parity
	}

	return ecc;
}

static uint32_t calculateECC(const std::vector<uint32_t>& data) {
	uint32_t ecc = 0;
	for (size_t ii = 0; ii < data.size(); ++ii) {
		ecc = xc7series::icap_ecc(ii, data[ii], ecc);
	}
	return ecc;
}

void updateECC(std::vector<uint32_t>& data) {
	assert(data.size() >= kECCFrameNumber);
	// Replace the old ECC with the new.
	data[kECCFrameNumber] &= 0xFFFFE000;
	data[kECCFrameNumber] |= (calculateECC(data) & 0x1FFF);
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
