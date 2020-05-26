/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/block_type.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

std::ostream& operator<<(std::ostream& o, BlockType value) {
	switch (value) {
		case BlockType::CLB_IO_CLK:
			o << "CLB/IO/CLK";
			break;
		case BlockType::BLOCK_RAM:
			o << "Block RAM";
			break;
		case BlockType::CFG_CLB:
			o << "Config CLB";
			break;
	}

	return o;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {

Node convert<prjxray::xilinx::xc7series::BlockType>::encode(
    const prjxray::xilinx::xc7series::BlockType& rhs) {
	switch (rhs) {
		case prjxray::xilinx::xc7series::BlockType::CLB_IO_CLK:
			return Node("CLB_IO_CLK");
		case prjxray::xilinx::xc7series::BlockType::BLOCK_RAM:
			return Node("BLOCK_RAM");
		case prjxray::xilinx::xc7series::BlockType::CFG_CLB:
			return Node("CFG_CLB");
		default:
			return Node(static_cast<unsigned int>(rhs));
	}
}

bool YAML::convert<prjxray::xilinx::xc7series::BlockType>::decode(
    const Node& node,
    prjxray::xilinx::xc7series::BlockType& lhs) {
	auto type_str = node.as<std::string>();

	if (type_str == "CLB_IO_CLK") {
		lhs = prjxray::xilinx::xc7series::BlockType::CLB_IO_CLK;
		return true;
	} else if (type_str == "BLOCK_RAM") {
		lhs = prjxray::xilinx::xc7series::BlockType::BLOCK_RAM;
		return true;
	} else if (type_str == "CFG_CLB") {
		lhs = prjxray::xilinx::xc7series::BlockType::CFG_CLB;
		return true;
	} else {
		return false;
	}
}

}  // namespace YAML
