/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_ECC_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_ECC_H_

#include <cstdint>
#include <vector>

namespace prjxray {
namespace xilinx {
namespace xc7series {

// Extend the current ECC code with one data word (32 bit) at a given
// word index in the configuration frame and return the new ECC code.
uint32_t icap_ecc(uint32_t idx, uint32_t data, uint32_t ecc);

// Updates the ECC information in the frame.
void updateECC(std::vector<uint32_t>& data);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_ECC_H_
