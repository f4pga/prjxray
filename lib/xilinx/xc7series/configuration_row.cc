/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/configuration_row.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

bool Row::IsValidFrameAddress(FrameAddress address) const {
	auto addr_bus = configuration_buses_.find(address.block_type());
	if (addr_bus == configuration_buses_.end())
		return false;
	return addr_bus->second.IsValidFrameAddress(address);
}

absl::optional<FrameAddress> Row::GetNextFrameAddress(
    FrameAddress address) const {
	// Find the bus for the current address.
	auto addr_bus = configuration_buses_.find(address.block_type());

	// If the current address isn't in a known bus, no way to know the next.
	if (addr_bus == configuration_buses_.end())
		return {};

	// Ask the bus for the next address.
	absl::optional<FrameAddress> next_address =
	    addr_bus->second.GetNextFrameAddress(address);
	if (next_address)
		return next_address;

	// The current bus doesn't know what the next address is. Rows come next
	// in frame address numerical order so punt back to the caller to figure
	// it out.
	return {};
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::Row>::encode(const xc7series::Row& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/row");
	node["configuration_buses"] = rhs.configuration_buses_;
	return node;
}

bool convert<xc7series::Row>::decode(const Node& node, xc7series::Row& lhs) {
	if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/row") {
		return false;
	}

	lhs.configuration_buses_ =
	    node["configuration_buses"]
	        .as<std::map<xc7series::BlockType,
	                     xc7series::ConfigurationBus>>();
	return true;
}

}  // namespace YAML
