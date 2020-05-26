/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <iostream>

#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_writer.h>

namespace prjxray {
namespace xilinx {

template <>
// Per UG380 pg 78: Bus Width Auto Detection
typename BitstreamWriter<Spartan6>::header_t BitstreamWriter<Spartan6>::header_{
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
    0xFFFF, 0xFFFF, 0xFFFF, 0xAA99, 0x5566};

// Per UG470 pg 80: Bus Width Auto Detection
template <>
typename BitstreamWriter<Series7>::header_t BitstreamWriter<Series7>::header_{
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x000000BB, 0x11220044,
    0xFFFFFFFF, 0xFFFFFFFF, 0xAA995566};

template <>
typename BitstreamWriter<UltraScale>::header_t
    BitstreamWriter<UltraScale>::header_{0xFFFFFFFF, 0x000000BB, 0x11220044,
                                         0xFFFFFFFF, 0xFFFFFFFF, 0xAA995566};

template <>
typename BitstreamWriter<UltraScalePlus>::header_t
    BitstreamWriter<UltraScalePlus>::header_{
        0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
        0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
        0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x000000BB, 0x11220044,
        0xFFFFFFFF, 0xFFFFFFFF, 0xAA995566};

uint32_t packet2header(
    const ConfigurationPacket<Spartan6ConfigurationRegister>& packet) {
	uint32_t ret = 0;

	ret = bit_field_set(ret, 15, 13, packet.header_type());

	switch (packet.header_type()) {
		case NONE:
			// Bitstreams are 0 padded sometimes, essentially making
			// a type 0 frame Ignore the other fields for now
			break;
		case TYPE1: {
			// Table 5-20: Type 1 Packet Header Format
			ret = bit_field_set(ret, 12, 11, packet.opcode());
			ret = bit_field_set(ret, 10, 5, packet.address());
			ret = bit_field_set(ret, 4, 0, packet.data().length());
			break;
		}
		case TYPE2: {
			// Table 5-22: Type 2 Packet Header
			ret = bit_field_set(ret, 12, 11, packet.opcode());
			ret = bit_field_set(ret, 10, 5, packet.address());
			break;
		}
		default:
			break;
	}

	return ret;
}

uint32_t packet2header(
    const ConfigurationPacket<Series7ConfigurationRegister>& packet) {
	uint32_t ret = 0;

	ret = bit_field_set(ret, 31, 29, packet.header_type());

	switch (packet.header_type()) {
		case NONE:
			// Bitstreams are 0 padded sometimes, essentially making
			// a type 0 frame Ignore the other fields for now
			break;
		case TYPE1: {
			// Table 5-20: Type 1 Packet Header Format
			ret = bit_field_set(ret, 28, 27, packet.opcode());
			ret = bit_field_set(ret, 26, 13, packet.address());
			ret = bit_field_set(ret, 10, 0, packet.data().length());
			break;
		}
		case TYPE2: {
			// Table 5-22: Type 2 Packet Header
			// Note address is from previous type 1 header
			ret = bit_field_set(ret, 28, 27, packet.opcode());
			ret = bit_field_set(ret, 26, 0, packet.data().length());
			break;
		}
		default:
			break;
	}

	return ret;
}

}  // namespace xilinx
}  // namespace prjxray
