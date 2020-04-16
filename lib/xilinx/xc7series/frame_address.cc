/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/frame_address.h>

#include <iomanip>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

FrameAddress::FrameAddress(BlockType block_type,
                           bool is_bottom_half_rows,
                           uint8_t row,
                           uint16_t column,
                           uint8_t minor) {
	address_ = bit_field_set(0, 25, 23, block_type);
	address_ = bit_field_set(address_, 22, 22, is_bottom_half_rows);
	address_ = bit_field_set(address_, 21, 17, row);
	address_ = bit_field_set(address_, 16, 7, column);
	address_ = bit_field_set(address_, 6, 0, minor);
}

BlockType FrameAddress::block_type() const {
	return static_cast<BlockType>(bit_field_get(address_, 25, 23));
}

bool FrameAddress::is_bottom_half_rows() const {
	return bit_field_get(address_, 22, 22);
}

uint8_t FrameAddress::row() const {
	return bit_field_get(address_, 21, 17);
}

uint16_t FrameAddress::column() const {
	return bit_field_get(address_, 16, 7);
}

uint8_t FrameAddress::minor() const {
	return bit_field_get(address_, 6, 0);
}

std::ostream& operator<<(std::ostream& o, const FrameAddress& addr) {
	o << "[" << std::hex << std::showbase << std::setw(10)
	  << static_cast<uint32_t>(addr) << "] "
	  << (addr.is_bottom_half_rows() ? "BOTTOM" : "TOP")
	  << " Row=" << std::setw(2) << std::dec
	  << static_cast<unsigned int>(addr.row()) << " Column=" << std::setw(2)
	  << std::dec << addr.column() << " Minor=" << std::setw(2) << std::dec
	  << static_cast<unsigned int>(addr.minor())
	  << " Type=" << addr.block_type();
	return o;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {

namespace xc7series = prjxray::xilinx::xc7series;

Node convert<xc7series::FrameAddress>::encode(
    const xc7series::FrameAddress& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/frame_address");
	node["block_type"] = rhs.block_type();
	node["row_half"] = (rhs.is_bottom_half_rows() ? "bottom" : "top");
	node["row"] = static_cast<unsigned int>(rhs.row());
	node["column"] = static_cast<unsigned int>(rhs.column());
	node["minor"] = static_cast<unsigned int>(rhs.minor());
	return node;
}

bool convert<xc7series::FrameAddress>::decode(const Node& node,
                                              xc7series::FrameAddress& lhs) {
	if (!(node.Tag() == "xilinx/xc7series/frame_address" ||
	      node.Tag() == "xilinx/xc7series/configuration_frame_address") ||
	    !node["block_type"] || !node["row_half"] || !node["row"] ||
	    !node["column"] || !node["minor"])
		return false;

	bool row_half;
	if (node["row_half"].as<std::string>() == "top") {
		row_half = false;
	} else if (node["row_half"].as<std::string>() == "bottom") {
		row_half = true;
	} else {
		return false;
	}

	lhs = prjxray::xilinx::xc7series::FrameAddress(
	    node["block_type"].as<xc7series::BlockType>(), row_half,
	    node["row"].as<unsigned int>(), node["column"].as<unsigned int>(),
	    node["minor"].as<unsigned int>());
	return true;
}

}  // namespace YAML
