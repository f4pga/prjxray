/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_CONFIGURATION_PACKET_WITH_PAYLOAD_H
#define PRJXRAY_LIB_XILINX_CONFIGURATION_PACKET_WITH_PAYLOAD_H

#include <memory>

#include <absl/types/span.h>
#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/configuration_register.h>

namespace prjxray {
namespace xilinx {

template <int Words, typename ConfigRegType>
class ConfigurationPacketWithPayload
    : public ConfigurationPacket<ConfigRegType> {
       public:
	ConfigurationPacketWithPayload(
	    typename ConfigurationPacket<ConfigRegType>::Opcode op,
	    ConfigRegType reg,
	    const std::array<uint32_t, Words>& payload)
	    : ConfigurationPacket<ConfigRegType>(
	          ConfigurationPacketType::TYPE1,
	          op,
	          reg,
	          absl::Span<uint32_t>(payload_)),
	      payload_(std::move(payload)) {}

       private:
	std::array<uint32_t, Words> payload_;
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_CONFIGURATION_PACKET_WITH_PAYLOAD_H
