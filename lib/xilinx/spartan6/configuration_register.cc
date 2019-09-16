#include <prjxray/xilinx/spartan6/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

std::ostream& operator<<(std::ostream& o, const ConfigurationRegister& value) {
	switch (value) {
		case ConfigurationRegister::CRC:
			return o << "CRC";
		case ConfigurationRegister::FAR_MAJ:
			return o << "Frame Address Register Block and Major";
		case ConfigurationRegister::FAR_MIN:
			return o << "Frame Address Register Minor";
		case ConfigurationRegister::FDRI:
			return o << "Frame Data Input";
		case ConfigurationRegister::FDRO:
			return o << "Frame Data Output";
		case ConfigurationRegister::CMD:
			return o << "Command";
		case ConfigurationRegister::CTL:
			return o << "Control";
		case ConfigurationRegister::MASK:
			return o << "Control Mask";
		case ConfigurationRegister::STAT:
			return o << "Status";
		case ConfigurationRegister::LOUT:
			return o << "Legacy Output";
		case ConfigurationRegister::COR1:
			return o << "Configuration Option 1";
		case ConfigurationRegister::COR2:
			return o << "Configuration Option 2";
		case ConfigurationRegister::PWRDN_REG:
			return o << "Power-down Option register";
		case ConfigurationRegister::FLR:
			return o << "Frame Length register";
		case ConfigurationRegister::IDCODE:
			return o << "Device ID";
		case ConfigurationRegister::CWDT:
			return o << "Watchdog Timer";
		case ConfigurationRegister::HC_OPT_REG:
			return o << "House Clean Option register";
		case ConfigurationRegister::CSBO:
			return o << "CSB output for parallel daisy-chaining";
		case ConfigurationRegister::GENERAL1:
			return o << "Power-up self test or loadable program "
			            "address";
		case ConfigurationRegister::GENERAL2:
			return o << "Power-up self test or loadable program "
			         << "address and new SPI opcode";
		case ConfigurationRegister::GENERAL3:
			return o << "Golden bitstream address";
		case ConfigurationRegister::GENERAL4:
			return o
			       << "Golden bitstream address and new SPI opcode";
		case ConfigurationRegister::GENERAL5:
			return o
			       << "User-defined register for fail-safe scheme";
		case ConfigurationRegister::MODE_REG:
			return o << "Reboot mode";
		case ConfigurationRegister::PU_GWE:
			return o << "GWE cycle during wake-up from suspend";
		case ConfigurationRegister::PU_GTS:
			return o << "GTS cycle during wake-up from suspend";
		case ConfigurationRegister::MFWR:
			return o << "Multi-frame write register";
		case ConfigurationRegister::CCLK_FREQ:
			return o << "CCLK frequency for master mode";
		case ConfigurationRegister::SEU_OPT:
			return o << "SEU frequency, enable and status";
		case ConfigurationRegister::EXP_SIGN:
			return o << "Expected readback signature for SEU "
			            "detection";
		case ConfigurationRegister::RDBK_SIGN:
			return o << "Readback signature for readback command "
			            "and SEU";
		case ConfigurationRegister::BOOTSTS:
			return o << "Boot History Register";
		case ConfigurationRegister::EYE_MASK:
			return o << "Mask pins for Multi-Pin Wake-Up";
		case ConfigurationRegister::CBC_REG:
			return o << "Initial CBC Value Register";
		default:
			return o << "Unknown";
	}
};

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray
