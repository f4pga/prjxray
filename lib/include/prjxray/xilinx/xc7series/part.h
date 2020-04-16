/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_

#include <algorithm>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include <absl/types/optional.h>
#include <prjxray/xilinx/xc7series/global_clock_region.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class Part {
       public:
	constexpr static uint32_t kInvalidIdcode = 0;

	static absl::optional<Part> FromFile(const std::string& path);

	// Constructs an invalid part with a zero IDCODE. Required for YAML
	// conversion but shouldn't be used otherwise.
	Part() : idcode_(kInvalidIdcode) {}

	template <typename T>
	Part(uint32_t idcode, T collection)
	    : Part(idcode, std::begin(collection), std::end(collection)) {}

	template <typename T>
	Part(uint32_t idcode, T first, T last);

	uint32_t idcode() const { return idcode_; }

	bool IsValidFrameAddress(FrameAddress address) const;

	absl::optional<FrameAddress> GetNextFrameAddress(
	    FrameAddress address) const;

       private:
	friend struct YAML::convert<Part>;

	uint32_t idcode_;
	GlobalClockRegion top_region_;
	GlobalClockRegion bottom_region_;
};

template <typename T>
Part::Part(uint32_t idcode, T first, T last) : idcode_(idcode) {
	auto first_of_top =
	    std::partition(first, last, [](const FrameAddress& addr) {
		    return addr.is_bottom_half_rows();
	    });

	top_region_ = GlobalClockRegion(first_of_top, last);
	bottom_region_ = GlobalClockRegion(first, first_of_top);
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::xc7series::Part> {
	static Node encode(const prjxray::xilinx::xc7series::Part& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::xc7series::Part& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_
