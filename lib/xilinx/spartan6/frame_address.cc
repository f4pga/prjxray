/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <iomanip>

#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/spartan6/frame_address.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

// According to UG380 pg. 101 the Frame Address Register (FAR)
// consists of two 16-bit registers (FAR MAJOR and FAR MINOR).
// We construct the 32-bit frame address from these two.
FrameAddress::FrameAddress(spartan6::BlockType block_type,
                           uint8_t row,
                           uint8_t column,
                           uint16_t minor) {
	address_ = bit_field_set(0, 31, 28, block_type);
	address_ =
	    bit_field_set(address_, 27, 24, row);  // high register, bit 8-11
	address_ =
	    bit_field_set(address_, 23, 16, column);  // high register, bits 0-7
	address_ =
	    bit_field_set(address_, 9, 0, minor);  // low register, bit 0-9
}

bool FrameAddress::is_bottom_half_rows() const {
	return false;
}

spartan6::BlockType FrameAddress::block_type() const {
	return static_cast<typename spartan6::BlockType>(
	    bit_field_get(address_, 31, 28));
}

uint8_t FrameAddress::row() const {
	return bit_field_get(address_, 27, 24);
}

uint8_t FrameAddress::column() const {
	return bit_field_get(address_, 23, 16);
}

uint16_t FrameAddress::minor() const {
	return bit_field_get(address_, 9, 0);
}

std::ostream& operator<<(std::ostream& o, const FrameAddress& addr) {
	o << "[" << std::hex << std::showbase << std::setw(10)
	  << static_cast<uint32_t>(addr) << "] "
	  << " Row=" << std::setw(2) << std::dec
	  << static_cast<unsigned int>(addr.row()) << "Column =" << std::setw(2)
	  << std::dec << addr.column() << " Minor=" << std::setw(2) << std::dec
	  << static_cast<unsigned int>(addr.minor())
	  << " Type=" << addr.block_type();
	return o;
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {

namespace spartan6 = prjxray::xilinx::spartan6;

Node convert<spartan6::FrameAddress>::encode(
    const spartan6::FrameAddress& rhs) {
	Node node;
	node.SetTag("xilinx/spartan6/frame_address");
	node["block_type"] = rhs.block_type();
	node["row"] = static_cast<unsigned int>(rhs.row());
	node["column"] = static_cast<unsigned int>(rhs.column());
	node["minor"] = static_cast<unsigned int>(rhs.minor());
	return node;
}

bool convert<spartan6::FrameAddress>::decode(const Node& node,
                                             spartan6::FrameAddress& lhs) {
	if (!(node.Tag() == "xilinx/spartan6/frame_address" ||
	      node.Tag() == "xilinx/spartan6/configuration_frame_address") ||
	    !node["block_type"] || !node["row"] || !node["column"] ||
	    !node["minor"])
		return false;

	lhs = spartan6::FrameAddress(
	    node["block_type"].as<spartan6::BlockType>(),
	    node["row"].as<unsigned int>(), node["column"].as<unsigned int>(),
	    node["minor"].as<unsigned int>());
	return true;
}

}  // namespace YAML
