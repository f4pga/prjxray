#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_NOP_PACKET_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_NOP_PACKET_H

#include <prjxray/xilinx/spartan6/configuration_packet.h>
#include <prjxray/xilinx/spartan6/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

class NopPacket : public ConfigurationPacket {
       public:
	NopPacket()
	    : ConfigurationPacket(1,
	                          Opcode::NOP,
	                          ConfigurationRegister::CRC,
	                          {}) {}
};

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_NOP_PACKET_H
