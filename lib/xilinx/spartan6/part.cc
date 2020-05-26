/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/xilinx/spartan6/part.h>

#include <iomanip>
#include <iostream>
#include <sstream>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

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
		next_address = FrameAddress(address.block_type(), 0, 0, 0);
		if (bottom_region_.IsValidFrameAddress(*next_address))
			return next_address;
	}

	// Block types are next numerically.
	if (address.block_type() < spartan6::BlockType::BLOCK_RAM) {
		next_address =
		    FrameAddress(spartan6::BlockType::BLOCK_RAM, 0, 0, 0);
		if (IsValidFrameAddress(*next_address))
			return next_address;
	}

	if (address.block_type() < spartan6::BlockType::IOB) {
		next_address = FrameAddress(spartan6::BlockType::IOB, 0, 0, 0);
		if (IsValidFrameAddress(*next_address))
			return next_address;
	}

	return {};
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace spartan6 = prjxray::xilinx::spartan6;

namespace YAML {

Node convert<spartan6::Part>::encode(const spartan6::Part& rhs) {
	Node node;
	node.SetTag("xilinx/spartan6/part");

	std::ostringstream idcode_str;
	idcode_str << "0x" << std::hex << rhs.idcode_;
	node["idcode"] = idcode_str.str();
	node["global_clock_regions"]["top"] = rhs.top_region_;
	node["global_clock_regions"]["bottom"] = rhs.bottom_region_;
	return node;
}

bool convert<spartan6::Part>::decode(const Node& node, spartan6::Part& lhs) {
	if (!node.Tag().empty() && node.Tag() != "xilinx/spartan6/part")
		return false;

	if (!node["global_clock_regions"] && !node["configuration_ranges"]) {
		return false;
	}

	lhs.idcode_ = node["idcode"].as<uint32_t>();

	if (node["global_clock_regions"]) {
		lhs.top_region_ = node["global_clock_regions"]["top"]
		                      .as<spartan6::GlobalClockRegion>();
		lhs.bottom_region_ = node["global_clock_regions"]["bottom"]
		                         .as<spartan6::GlobalClockRegion>();
	} else if (node["configuration_ranges"]) {
		std::vector<spartan6::FrameAddress> addresses;
		for (auto range : node["configuration_ranges"]) {
			auto begin =
			    range["begin"].as<spartan6::FrameAddress>();
			auto end = range["end"].as<spartan6::FrameAddress>();
			for (uint32_t cur = begin; cur < end; ++cur) {
				addresses.push_back(cur);
			}
		}

		lhs = spartan6::Part(lhs.idcode_, addresses);
	}

	return true;
};

}  // namespace YAML
