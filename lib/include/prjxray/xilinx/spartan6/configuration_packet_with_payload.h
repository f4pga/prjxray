#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_g_CONFIGURATION_PACKET_WITH_PAYLOAD_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_g_CONFIGURATION_PACKET_WITH_PAYLOAD_H

#include <memory>

#include <absl/types/span.h>
#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/spartan6/configuration_packet.h>
#include <prjxray/xilinx/spartan6/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

template <int Words>
class ConfigurationPacketWithPayload : public ConfigurationPacket {
       public:
	ConfigurationPacketWithPayload(
	    Opcode op,
	    ConfigurationRegister reg,
	    const std::array<uint32_t, Words>& payload)
	    : ConfigurationPacket(1, op, reg, absl::Span<uint32_t>(payload_)),
	      payload_(std::move(payload)) {}

       private:
	std::array<uint32_t, Words> payload_;
};  // namespace spartan6

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_g_CONFIGURATION_PACKET_WITH_PAYLOAD_H
