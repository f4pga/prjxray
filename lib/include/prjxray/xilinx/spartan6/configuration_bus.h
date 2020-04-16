/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_SPARTAN6_CONFIGURATION_BUS_H_
#define PRJXRAY_LIB_XILINX_SPARTAN6_CONFIGURATION_BUS_H_

#include <algorithm>
#include <cassert>
#include <map>
#include <memory>

#include <absl/types/optional.h>
#include <prjxray/xilinx/spartan6/configuration_column.h>
#include <prjxray/xilinx/spartan6/frame_address.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

// ConfigurationBus represents a bus for sending frames to a specific BlockType
// within a Row.  An instance of ConfigurationBus will contain one or more
// ConfigurationColumns.
class ConfigurationBus {
       public:
	ConfigurationBus() = default;

	// Constructs a ConfigurationBus from iterators yielding
	// FrameAddresses.  The frame address need not be contiguous or sorted
	// but they must all have the same block type, row half, and row
	// address components.
	template <typename T>
	ConfigurationBus(T first, T last);

	// Returns true if the provided address falls into a valid segment of
	// the address range on this bus.  Only the column and minor components
	// of the address are considered as all other components are outside
	// the scope of a bus.
	bool IsValidFrameAddress(FrameAddress address) const;

	// Returns the next valid address on the bus in numerically increasing
	// order. If the next address would fall outside this bus, no object is
	// returned.
	absl::optional<FrameAddress> GetNextFrameAddress(
	    FrameAddress address) const;

       private:
	friend struct YAML::convert<ConfigurationBus>;

	std::map<unsigned int, ConfigurationColumn> configuration_columns_;
};

template <typename T>
ConfigurationBus::ConfigurationBus(T first, T last) {
	assert(
	    std::all_of(first, last, [&](const typename T::value_type& addr) {
		    return (addr.block_type() == first->block_type() &&
		            addr.row() == first->row());
	    }));

	std::sort(first, last,
	          [](const FrameAddress& lhs, const FrameAddress& rhs) {
		          return lhs.column() < rhs.column();
	          });

	for (auto col_first = first; col_first != last;) {
		auto col_last = std::upper_bound(
		    col_first, last, col_first->column(),
		    [](const unsigned int& lhs, const FrameAddress& rhs) {
			    return lhs < rhs.column();
		    });

		configuration_columns_.emplace(
		    col_first->column(),
		    std::move(ConfigurationColumn(col_first, col_last)));
		col_first = col_last;
	}
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::spartan6::ConfigurationBus> {
	static Node encode(
	    const prjxray::xilinx::spartan6::ConfigurationBus& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::spartan6::ConfigurationBus& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_SPARTAN6_CONFIGURATION_BUS_H_
