#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_REGISTER_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_REGISTER_H_

#include <ostream>

namespace prjxray {
namespace xilinx {
namespace xc7series {

enum class ConfigurationRegister : unsigned int {
	CRC     = 0b00000,
	FAR     = 0b00001,
	FDRI    = 0b00010,
	FDRO    = 0b00011,
	CMD     = 0b00100,
	CTL0    = 0b00101,
	MASK    = 0b00110,
	STAT    = 0b00111,
	LOUT    = 0b01000,
	COR0    = 0b01001,
	MFWR    = 0b01010,
	CBC     = 0b01011,
	IDCODE  = 0b01100,
	AXSS    = 0b01101,
	COR1    = 0b01110,
	WBSTAR  = 0b10000,
	TIMER   = 0b10001,
	BOOTSTS = 0b10110,
	CTL1    = 0b11000,
	BSPI    = 0b11111,
};

std::ostream& operator<<(std::ostream &o, const ConfigurationRegister &value);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_REGISTER_H_
