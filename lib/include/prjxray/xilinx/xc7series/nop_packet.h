#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_NOP_PACKET_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_NOP_PACKET_H

#include <prjxray/xilinx/xc7series/configuration_packet.h>
#include <prjxray/xilinx/xc7series/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class NopPacket : public ConfigurationPacket {
       public:
	NopPacket()
	    : ConfigurationPacket(1,
	                          Opcode::NOP,
	                          ConfigurationRegister::CRC,
	                          {}) {}
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_NOP_PACKET_H
