/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/xc7series/part.h>

#include <iomanip>
#include <sstream>

namespace prjxray {
namespace xilinx {
namespace xc7series {

absl::optional<Part> Part::FromFile(const std::string& path) {
	try {
		YAML::Node yaml = YAML::LoadFile(path);
		return yaml.as<Part>();
	} catch (YAML::Exception& e) {
		return {};
	}
}

bool Part::IsValidFrameAddress(FrameAddress address) const {
	if (address.is_bottom_half_rows()) {
		return bottom_region_.IsValidFrameAddress(address);
	} else {
		return top_region_.IsValidFrameAddress(address);
	}
}

absl::optional<FrameAddress> Part::GetNextFrameAddress(
    FrameAddress address) const {
	// Ask the current global clock region first.
	absl::optional<FrameAddress> next_address =
	    (address.is_bottom_half_rows()
	         ? bottom_region_.GetNextFrameAddress(address)
	         : top_region_.GetNextFrameAddress(address));
	if (next_address)
		return next_address;

	// If the current address is in the top region, the bottom region is
	// next numerically.
	if (!address.is_bottom_half_rows()) {
		next_address =
		    FrameAddress(address.block_type(), true, 0, 0, 0);
		if (bottom_region_.IsValidFrameAddress(*next_address))
			return next_address;
	}

	// Block types are next numerically.
	if (address.block_type() < BlockType::BLOCK_RAM) {
		next_address =
		    FrameAddress(BlockType::BLOCK_RAM, false, 0, 0, 0);
		if (IsValidFrameAddress(*next_address))
			return next_address;
	}

	if (address.block_type() < BlockType::CFG_CLB) {
		next_address = FrameAddress(BlockType::CFG_CLB, false, 0, 0, 0);
		if (IsValidFrameAddress(*next_address))
			return next_address;
	}

	return {};
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::Part>::encode(const xc7series::Part& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/part");

	std::ostringstream idcode_str;
	idcode_str << "0x" << std::hex << rhs.idcode_;
	node["idcode"] = idcode_str.str();
	node["global_clock_regions"]["top"] = rhs.top_region_;
	node["global_clock_regions"]["bottom"] = rhs.bottom_region_;
	return node;
}

bool convert<xc7series::Part>::decode(const Node& node, xc7series::Part& lhs) {
	if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/part")
		return false;

	if (!node["global_clock_regions"] && !node["configuration_ranges"]) {
		return false;
	}

	lhs.idcode_ = node["idcode"].as<uint32_t>();

	if (node["global_clock_regions"]) {
		lhs.top_region_ = node["global_clock_regions"]["top"]
		                      .as<xc7series::GlobalClockRegion>();
		lhs.bottom_region_ = node["global_clock_regions"]["bottom"]
		                         .as<xc7series::GlobalClockRegion>();
	} else if (node["configuration_ranges"]) {
		std::vector<xc7series::FrameAddress> addresses;
		for (auto range : node["configuration_ranges"]) {
			auto begin =
			    range["begin"].as<xc7series::FrameAddress>();
			auto end = range["end"].as<xc7series::FrameAddress>();
			for (uint32_t cur = begin; cur < end; ++cur) {
				addresses.push_back(cur);
			}
		}

		lhs = xc7series::Part(lhs.idcode_, addresses);
	}

	return true;
};

}  // namespace YAML
