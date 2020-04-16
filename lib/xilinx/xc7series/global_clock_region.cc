/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/global_clock_region.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

bool GlobalClockRegion::IsValidFrameAddress(FrameAddress address) const {
	auto addr_row = rows_.find(address.row());
	if (addr_row == rows_.end())
		return false;
	return addr_row->second.IsValidFrameAddress(address);
}

absl::optional<FrameAddress> GlobalClockRegion::GetNextFrameAddress(
    FrameAddress address) const {
	// Find the row for the current address.
	auto addr_row = rows_.find(address.row());

	// If the current address isn't in a known row, no way to know the next.
	if (addr_row == rows_.end())
		return {};

	// Ask the row for the next address.
	absl::optional<FrameAddress> next_address =
	    addr_row->second.GetNextFrameAddress(address);
	if (next_address)
		return next_address;

	// The current row doesn't know what the next address is.  Assume that
	// the next valid address is the beginning of the next row.
	if (++addr_row != rows_.end()) {
		auto next_address = FrameAddress(address.block_type(),
		                                 address.is_bottom_half_rows(),
		                                 addr_row->first, 0, 0);
		if (addr_row->second.IsValidFrameAddress(next_address))
			return next_address;
	}

	// Must be in a different global clock region.
	return {};
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::GlobalClockRegion>::encode(
    const xc7series::GlobalClockRegion& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/global_clock_region");
	node["rows"] = rhs.rows_;
	return node;
}

bool convert<xc7series::GlobalClockRegion>::decode(
    const Node& node,
    xc7series::GlobalClockRegion& lhs) {
	if (!node.Tag().empty() &&
	    node.Tag() != "xilinx/xc7series/global_clock_region") {
		return false;
	}

	lhs.rows_ = node["rows"].as<std::map<unsigned int, xc7series::Row>>();
	return true;
}

}  // namespace YAML
