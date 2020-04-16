/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/spartan6/block_type.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

std::ostream& operator<<(std::ostream& o, BlockType value) {
	switch (value) {
		case BlockType::CLB_IOI_CLK:
			o << "CLB/IOI/CLK";
			break;
		case BlockType::BLOCK_RAM:
			o << "Block RAM";
			break;
		case BlockType::IOB:
			o << "Config CLB";
			break;
	}

	return o;
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {

Node convert<prjxray::xilinx::spartan6::BlockType>::encode(
    const prjxray::xilinx::spartan6::BlockType& rhs) {
	switch (rhs) {
		case prjxray::xilinx::spartan6::BlockType::CLB_IOI_CLK:
			return Node("CLB_IOI_CLK");
		case prjxray::xilinx::spartan6::BlockType::BLOCK_RAM:
			return Node("BLOCK_RAM");
		case prjxray::xilinx::spartan6::BlockType::IOB:
			return Node("IOB");
		default:
			return Node(static_cast<unsigned int>(rhs));
	}
}

bool YAML::convert<prjxray::xilinx::spartan6::BlockType>::decode(
    const Node& node,
    prjxray::xilinx::spartan6::BlockType& lhs) {
	auto type_str = node.as<std::string>();

	if (type_str == "CLB_IOI_CLK") {
		lhs = prjxray::xilinx::spartan6::BlockType::CLB_IOI_CLK;
		return true;
	} else if (type_str == "BLOCK_RAM") {
		lhs = prjxray::xilinx::spartan6::BlockType::BLOCK_RAM;
		return true;
	} else if (type_str == "IOB") {
		lhs = prjxray::xilinx::spartan6::BlockType::IOB;
		return true;
	} else {
		return false;
	}
}

}  // namespace YAML
