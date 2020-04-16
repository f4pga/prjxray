/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/configuration_register.h>

namespace prjxray {
namespace xilinx {

std::ostream& operator<<(std::ostream& o,
                         const Spartan6ConfigurationRegister& value) {
	switch (value) {
		case Spartan6ConfigurationRegister::CRC:
			return o << "CRC";
		case Spartan6ConfigurationRegister::FAR_MAJ:
			return o << "Frame Address Register Block and Major";
		case Spartan6ConfigurationRegister::FAR_MIN:
			return o << "Frame Address Register Minor";
		case Spartan6ConfigurationRegister::FDRI:
			return o << "Frame Data Input";
		case Spartan6ConfigurationRegister::FDRO:
			return o << "Frame Data Output";
		case Spartan6ConfigurationRegister::CMD:
			return o << "Command";
		case Spartan6ConfigurationRegister::CTL:
			return o << "Control";
		case Spartan6ConfigurationRegister::MASK:
			return o << "Control Mask";
		case Spartan6ConfigurationRegister::STAT:
			return o << "Status";
		case Spartan6ConfigurationRegister::LOUT:
			return o << "Legacy Output";
		case Spartan6ConfigurationRegister::COR1:
			return o << "Configuration Option 1";
		case Spartan6ConfigurationRegister::COR2:
			return o << "Configuration Option 2";
		case Spartan6ConfigurationRegister::PWRDN_REG:
			return o << "Power-down Option register";
		case Spartan6ConfigurationRegister::FLR:
			return o << "Frame Length register";
		case Spartan6ConfigurationRegister::IDCODE:
			return o << "Device ID";
		case Spartan6ConfigurationRegister::CWDT:
			return o << "Watchdog Timer";
		case Spartan6ConfigurationRegister::HC_OPT_REG:
			return o << "House Clean Option register";
		case Spartan6ConfigurationRegister::CSBO:
			return o << "CSB output for parallel daisy-chaining";
		case Spartan6ConfigurationRegister::GENERAL1:
			return o << "Power-up self test or loadable program "
			            "address";
		case Spartan6ConfigurationRegister::GENERAL2:
			return o << "Power-up self test or loadable program "
			         << "address and new SPI opcode";
		case Spartan6ConfigurationRegister::GENERAL3:
			return o << "Golden bitstream address";
		case Spartan6ConfigurationRegister::GENERAL4:
			return o
			       << "Golden bitstream address and new SPI opcode";
		case Spartan6ConfigurationRegister::GENERAL5:
			return o
			       << "User-defined register for fail-safe scheme";
		case Spartan6ConfigurationRegister::MODE_REG:
			return o << "Reboot mode";
		case Spartan6ConfigurationRegister::PU_GWE:
			return o << "GWE cycle during wake-up from suspend";
		case Spartan6ConfigurationRegister::PU_GTS:
			return o << "GTS cycle during wake-up from suspend";
		case Spartan6ConfigurationRegister::MFWR:
			return o << "Multi-frame write register";
		case Spartan6ConfigurationRegister::CCLK_FREQ:
			return o << "CCLK frequency for master mode";
		case Spartan6ConfigurationRegister::SEU_OPT:
			return o << "SEU frequency, enable and status";
		case Spartan6ConfigurationRegister::EXP_SIGN:
			return o << "Expected readback signature for SEU "
			            "detection";
		case Spartan6ConfigurationRegister::RDBK_SIGN:
			return o << "Readback signature for readback command "
			            "and SEU";
		case Spartan6ConfigurationRegister::BOOTSTS:
			return o << "Boot History Register";
		case Spartan6ConfigurationRegister::EYE_MASK:
			return o << "Mask pins for Multi-Pin Wake-Up";
		case Spartan6ConfigurationRegister::CBC_REG:
			return o << "Initial CBC Value Register";
		default:
			return o << "Unknown";
	}
}

std::ostream& operator<<(std::ostream& o,
                         const Series7ConfigurationRegister& value) {
	switch (value) {
		case Series7ConfigurationRegister::CRC:
			return o << "CRC";
		case Series7ConfigurationRegister::FAR:
			return o << "Frame Address";
		case Series7ConfigurationRegister::FDRI:
			return o << "Frame Data Input";
		case Series7ConfigurationRegister::FDRO:
			return o << "Frame Data Output";
		case Series7ConfigurationRegister::CMD:
			return o << "Command";
		case Series7ConfigurationRegister::CTL0:
			return o << "Control 0";
		case Series7ConfigurationRegister::MASK:
			return o << "Mask for CTL0 and CTL1";
		case Series7ConfigurationRegister::STAT:
			return o << "Status";
		case Series7ConfigurationRegister::LOUT:
			return o << "Legacy Output";
		case Series7ConfigurationRegister::COR0:
			return o << "Configuration Option 0";
		case Series7ConfigurationRegister::MFWR:
			return o << "Multiple Frame Write";
		case Series7ConfigurationRegister::CBC:
			return o << "Initial CBC Value";
		case Series7ConfigurationRegister::IDCODE:
			return o << "Device ID";
		case Series7ConfigurationRegister::AXSS:
			return o << "User Access";
		case Series7ConfigurationRegister::COR1:
			return o << "Configuration Option 1";
		case Series7ConfigurationRegister::WBSTAR:
			return o << "Warm Boot Start Address";
		case Series7ConfigurationRegister::TIMER:
			return o << "Watchdog Timer";
		case Series7ConfigurationRegister::BOOTSTS:
			return o << "Boot History Status";
		case Series7ConfigurationRegister::CTL1:
			return o << "Control 1";
		case Series7ConfigurationRegister::BSPI:
			return o << "BPI/SPI Configuration Options";
		default:
			return o << "Unknown";
	}
}

}  // namespace xilinx
}  // namespace prjxray
