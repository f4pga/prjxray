#include <prjxray/xilinx/xc7series/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

std::ostream& operator<<(std::ostream& o, const ConfigurationRegister& value) {
	switch (value) {
		case ConfigurationRegister::CRC:
			return o << "CRC";
		case ConfigurationRegister::FAR:
			return o << "Frame Address";
		case ConfigurationRegister::FDRI:
			return o << "Frame Data Input";
		case ConfigurationRegister::FDRO:
			return o << "Frame Data Output";
		case ConfigurationRegister::CMD:
			return o << "Command";
		case ConfigurationRegister::CTL0:
			return o << "Control 0";
		case ConfigurationRegister::MASK:
			return o << "Mask for CTL0 and CTL1";
		case ConfigurationRegister::STAT:
			return o << "Status";
		case ConfigurationRegister::LOUT:
			return o << "Legacy Output";
		case ConfigurationRegister::COR0:
			return o << "Configuration Option 0";
		case ConfigurationRegister::MFWR:
			return o << "Multiple Frame Write";
		case ConfigurationRegister::CBC:
			return o << "Initial CBC Value";
		case ConfigurationRegister::IDCODE:
			return o << "Device ID";
		case ConfigurationRegister::AXSS:
			return o << "User Access";
		case ConfigurationRegister::COR1:
			return o << "Configuration Option 1";
		case ConfigurationRegister::WBSTAR:
			return o << "Warm Boot Start Address";
		case ConfigurationRegister::TIMER:
			return o << "Watchdog Timer";
		case ConfigurationRegister::BOOTSTS:
			return o << "Boot History Status";
		case ConfigurationRegister::CTL1:
			return o << "Control 1";
		case ConfigurationRegister::BSPI:
			return o << "BPI/SPI Configuration Options";
		default:
			return o << "Unknown";
	}
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
