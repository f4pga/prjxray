/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/configuration_column.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

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

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::ConfigurationColumn>::encode(
    const xc7series::ConfigurationColumn& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/configuration_column");
	node["frame_count"] = rhs.frame_count_;
	return node;
}

bool convert<xc7series::ConfigurationColumn>::decode(
    const Node& node,
    xc7series::ConfigurationColumn& lhs) {
	if (!node.Tag().empty() &&
	    node.Tag() != "xilinx/xc7series/configuration_column") {
		return false;
	}

	lhs.frame_count_ = node["frame_count"].as<unsigned int>();
	return true;
}

}  // namespace YAML
