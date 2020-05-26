/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_SPARTAN6_CONFIGURATION_COLUMN_H_
#define PRJXRAY_LIB_XILINX_SPARTAN6_CONFIGURATION_COLUMN_H_

#include <algorithm>
#include <cassert>

#include <absl/types/optional.h>
#include <prjxray/xilinx/spartan6/frame_address.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

// ConfigurationColumn represents an endpoint on a ConfigurationBus.
class ConfigurationColumn {
       public:
	ConfigurationColumn() = default;
	ConfigurationColumn(unsigned int frame_count)
	    : frame_count_(frame_count) {}

	// Returns a ConfigurationColumn that describes a continguous range of
	// minor addresses that encompasses the given
	// FrameAddresses.  The provided addresses must only
	// differ only by their minor addresses.
	template <typename T>
	ConfigurationColumn(T first, T last);

	// Returns true if the minor field of the address is within the valid
	// range of this column.
	bool IsValidFrameAddress(FrameAddress address) const;

	// Returns the next address in numerical order.  If the next address
	// would be outside this column, return no object.
	absl::optional<FrameAddress> GetNextFrameAddress(
	    FrameAddress address) const;

       private:
	friend struct YAML::convert<ConfigurationColumn>;

	unsigned int frame_count_;
};

template <typename T>
ConfigurationColumn::ConfigurationColumn(T first, T last) {
	assert(
	    std::all_of(first, last, [&](const typename T::value_type& addr) {
		    return (addr.block_type() == first->block_type() &&
		            addr.row() == first->row() &&
		            addr.column() == first->column());
	    }));

	auto max_minor = std::max_element(
	    first, last, [](const FrameAddress& lhs, const FrameAddress& rhs) {
		    return lhs.minor() < rhs.minor();
	    });

	frame_count_ = max_minor->minor() + 1;
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::spartan6::ConfigurationColumn> {
	static Node encode(
	    const prjxray::xilinx::spartan6::ConfigurationColumn& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::spartan6::ConfigurationColumn& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_SPARTAN6_CONFIGURATION_COLUMN_H_
