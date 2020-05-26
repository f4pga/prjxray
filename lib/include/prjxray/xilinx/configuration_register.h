/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_CONFIGURATION_REGISTER_H_
#define PRJXRAY_LIB_XILINX_CONFIGURATION_REGISTER_H_

#include <ostream>

namespace prjxray {
namespace xilinx {

// Spartan6 configuration register addresses
// according to UG380, pg. 100
enum class Spartan6ConfigurationRegister : unsigned int {
	CRC = 0x00,
	FAR = 0x01,
	FAR_MAJ = 0x01,
	FAR_MIN = 0x02,
	FDRI = 0x03,
	FDRO = 0x04,
	CMD = 0x05,
	CTL = 0x06,
	CTL1 = 0x06,
	MASK = 0x07,
	STAT = 0x08,
	LOUT = 0x09,
	COR1 = 0x0a,
	COR2 = 0x0b,
	PWRDN_REG = 0x0c,
	FLR = 0x0d,
	IDCODE = 0x0e,
	CWDT = 0x0f,
	HC_OPT_REG = 0x10,
	CSBO = 0x12,
	GENERAL1 = 0x13,
	GENERAL2 = 0x14,
	GENERAL3 = 0x15,
	GENERAL4 = 0x16,
	GENERAL5 = 0x17,
	MODE_REG = 0x18,
	PU_GWE = 0x19,
	PU_GTS = 0x1a,
	MFWR = 0x1b,
	CCLK_FREQ = 0x1c,
	SEU_OPT = 0x1d,
	EXP_SIGN = 0x1e,
	RDBK_SIGN = 0x1f,
	BOOTSTS = 0x20,
	EYE_MASK = 0x21,
	CBC_REG = 0x22,
};

// Series-7 configuration register addresses
// according to UG470, pg. 109
enum class Series7ConfigurationRegister : unsigned int {
	CRC = 0x00,
	FAR = 0x01,
	FDRI = 0x02,
	FDRO = 0x03,
	CMD = 0x04,
	CTL0 = 0x05,
	MASK = 0x06,
	STAT = 0x07,
	LOUT = 0x08,
	COR0 = 0x09,
	MFWR = 0x0a,
	CBC = 0x0b,
	IDCODE = 0x0c,
	AXSS = 0x0d,
	COR1 = 0x0e,
	WBSTAR = 0x10,
	TIMER = 0x11,
	UNKNOWN = 0x13,
	BOOTSTS = 0x16,
	CTL1 = 0x18,
	BSPI = 0x1F,
};

std::ostream& operator<<(std::ostream& o,
                         const Spartan6ConfigurationRegister& value);
std::ostream& operator<<(std::ostream& o,
                         const Series7ConfigurationRegister& value);

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_CONFIGURATION_REGISTER_H_
