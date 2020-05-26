/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/configuration_bus.h>

#include <iostream>

namespace prjxray {
namespace xilinx {
namespace xc7series {

bool ConfigurationBus::IsValidFrameAddress(FrameAddress address) const {
	auto addr_column = configuration_columns_.find(address.column());
	if (addr_column == configuration_columns_.end())
		return false;

	return addr_column->second.IsValidFrameAddress(address);
}

absl::optional<FrameAddress> ConfigurationBus::GetNextFrameAddress(
    FrameAddress address) const {
	// Find the column for the current address.
	auto addr_column = configuration_columns_.find(address.column());

	// If the current address isn't in a known column, no way to know the
	// next address.
	if (addr_column == configuration_columns_.end())
		return {};

	// Ask the column for the next address.
	absl::optional<FrameAddress> next_address =
	    addr_column->second.GetNextFrameAddress(address);
	if (next_address)
		return next_address;

	// The current column doesn't know what the next address is.  Assume
	// that the next valid address is the beginning of the next column.
	if (++addr_column != configuration_columns_.end()) {
		auto next_address = FrameAddress(
		    address.block_type(), address.is_bottom_half_rows(),
		    address.row(), addr_column->first, 0);
		if (addr_column->second.IsValidFrameAddress(next_address))
			return next_address;
	}

	// Not in this bus.
	return {};
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::ConfigurationBus>::encode(
    const xc7series::ConfigurationBus& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/configuration_bus");
	node["configuration_columns"] = rhs.configuration_columns_;
	return node;
}

bool convert<xc7series::ConfigurationBus>::decode(
    const Node& node,
    xc7series::ConfigurationBus& lhs) {
	if (!node.Tag().empty() &&
	    node.Tag() != "xilinx/xc7series/configuration_bus") {
		return false;
	}

	lhs.configuration_columns_ =
	    node["configuration_columns"]
	        .as<std::map<unsigned int, xc7series::ConfigurationColumn>>();
	return true;
}

}  // namespace YAML
