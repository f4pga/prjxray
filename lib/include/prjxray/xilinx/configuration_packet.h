/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_CONFIGURATION_PACKET_H
#define PRJXRAY_LIB_XILINX_CONFIGURATION_PACKET_H

#include <cstdint>
#include <ostream>

#include <absl/types/optional.h>
#include <absl/types/span.h>
#include <prjxray/xilinx/configuration_register.h>

namespace prjxray {
namespace xilinx {

// As described in the configuration user guide for Series-7
// (UG470, pg. 108) there are two types of configuration packets
enum ConfigurationPacketType { NONE, TYPE1, TYPE2 };

// Creates a Type1 or Type2 configuration packet.
// Specification of the packets for Series-7 can be found in UG470, pg. 108
// For Spartan6 UG380, pg. 98
template <typename ConfigRegType>
class ConfigurationPacket {
       public:
	typedef std::pair<absl::Span<uint32_t>,
	                  absl::optional<ConfigurationPacket<ConfigRegType>>>
	    ParseResult;

	// Opcodes as specified in UG470 page 108
	enum Opcode {
		NOP = 0,
		Read = 1,
		Write = 2,
		/* reserved = 3 */
	};

	ConfigurationPacket(unsigned int header_type,
	                    Opcode opcode,
	                    ConfigRegType address,
	                    const absl::Span<const uint32_t>& data)
	    : header_type_(header_type),
	      opcode_(opcode),
	      address_(address),
	      data_(std::move(data)) {}

	unsigned int header_type() const { return header_type_; }
	const Opcode opcode() const { return opcode_; }
	const ConfigRegType address() const { return address_; }
	const absl::Span<const uint32_t>& data() const { return data_; }
	static ParseResult InitWithWords(
	    absl::Span<uint32_t> words,
	    const ConfigurationPacket<ConfigRegType>* previous_packet =
	        nullptr);

       private:
	unsigned int header_type_;
	Opcode opcode_;
	ConfigRegType address_;
	absl::Span<const uint32_t> data_;
};

template <class ConfigRegType>
std::ostream& operator<<(std::ostream& o,
                         const ConfigurationPacket<ConfigRegType>& packet);

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_CONFIGURATION_PACKET_H
