#include <prjxray/xilinx/configuration_register.h>

namespace prjxray {
namespace xilinx {

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
