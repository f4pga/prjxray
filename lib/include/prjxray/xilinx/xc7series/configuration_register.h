#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_REGISTER_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_REGISTER_H_

#include <ostream>

namespace prjxray {
namespace xilinx {
namespace xc7series {

enum class ConfigurationRegister : unsigned int {
	CRC     = 0x00,
	FAR     = 0x01,
	FDRI    = 0x02,
	FDRO    = 0x03,
	CMD     = 0x04,
	CTL0    = 0x05,
	MASK    = 0x06,
	STAT    = 0x07,
	LOUT    = 0x08,
	COR0    = 0x09,
	MFWR    = 0x0a,
	CBC     = 0x0b,
	IDCODE  = 0x0c,
	AXSS    = 0x0d,
	COR1    = 0x0e,
	WBSTAR  = 0x10,
	TIMER   = 0x11,
	BOOTSTS = 0x16,
	CTL1    = 0x18,
	BSPI    = 0x1F,
};

std::ostream& operator<<(std::ostream &o, const ConfigurationRegister &value);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_REGISTER_H_
