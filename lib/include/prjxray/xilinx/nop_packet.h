#ifndef PRJXRAY_LIB_XILINX_NOP_PACKET_H
#define PRJXRAY_LIB_XILINX_NOP_PACKET_H

#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/configuration_register.h>

namespace prjxray {
namespace xilinx {

template <typename ConfigRegType>
class NopPacket : public ConfigurationPacket<ConfigRegType> {
       public:
	NopPacket()
	    : ConfigurationPacket<ConfigRegType>(
	          ConfigurationPacketType::TYPE1,
	          ConfigurationPacket<ConfigRegType>::Opcode::NOP,
	          ConfigRegType::CRC,
	          {}) {}
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_NOP_PACKET_H
