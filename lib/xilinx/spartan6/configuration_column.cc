/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/spartan6/configuration_column.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

bool ConfigurationColumn::IsValidFrameAddress(FrameAddress address) const {
	return address.minor() < frame_count_;
}

absl::optional<FrameAddress> ConfigurationColumn::GetNextFrameAddress(
    FrameAddress address) const {
	if (!IsValidFrameAddress(address))
		return {};

	if (static_cast<unsigned int>(address.minor() + 1) < frame_count_) {
		return address + 1;
	}

	// Next address is not in this column.
	return {};
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace spartan6 = prjxray::xilinx::spartan6;

namespace YAML {

Node convert<spartan6::ConfigurationColumn>::encode(
    const spartan6::ConfigurationColumn& rhs) {
	Node node;
	node.SetTag("xilinx/spartan6/configuration_column");
	node["frame_count"] = rhs.frame_count_;
	return node;
}

bool convert<spartan6::ConfigurationColumn>::decode(
    const Node& node,
    spartan6::ConfigurationColumn& lhs) {
	if (!node.Tag().empty() &&
	    node.Tag() != "xilinx/spartan6/configuration_column") {
		return false;
	}

	lhs.frame_count_ = node["frame_count"].as<unsigned int>();
	return true;
}

}  // namespace YAML
