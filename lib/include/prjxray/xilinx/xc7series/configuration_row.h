/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_ROW_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_ROW_H_

#include <algorithm>
#include <cassert>
#include <map>
#include <memory>

#include <absl/types/optional.h>
#include <prjxray/xilinx/xc7series/block_type.h>
#include <prjxray/xilinx/xc7series/configuration_bus.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class Row {
       public:
	Row() = default;

	// Construct a row from a range of iterators that yield FrameAddresses.
	// The addresses may be noncontinguous and/or unsorted but all must
	// share the same row half and row components.
	template <typename T>
	Row(T first, T last);

	// Returns true if the provided address falls within a valid range
	// attributed to this row.  Only the block type, column, and minor
	// address components are considerd as the remaining components are
	// outside the scope of a row.
	bool IsValidFrameAddress(FrameAddress address) const;

	// Returns the next numerically increasing address within the Row. If
	// the next address would fall outside the Row, no object is returned.
	// If the next address would cross from one block type to another, no
	// object is returned as other rows of the same block type come before
	// other block types numerically.
	absl::optional<FrameAddress> GetNextFrameAddress(
	    FrameAddress address) const;

       private:
	friend struct YAML::convert<Row>;

	std::map<BlockType, ConfigurationBus> configuration_buses_;
};

template <typename T>
Row::Row(T first, T last) {
	assert(
	    std::all_of(first, last, [&](const typename T::value_type& addr) {
		    return (addr.is_bottom_half_rows() ==
		                first->is_bottom_half_rows() &&
		            addr.row() == first->row());
	    }));

	std::sort(first, last,
	          [](const FrameAddress& lhs, const FrameAddress& rhs) {
		          return lhs.block_type() < rhs.block_type();
	          });

	for (auto bus_first = first; bus_first != last;) {
		auto bus_last = std::upper_bound(
		    bus_first, last, bus_first->block_type(),
		    [](const BlockType& lhs, const FrameAddress& rhs) {
			    return lhs < rhs.block_type();
		    });

		configuration_buses_.emplace(
		    bus_first->block_type(),
		    std::move(ConfigurationBus(bus_first, bus_last)));
		bus_first = bus_last;
	}
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::xc7series::Row> {
	static Node encode(const prjxray::xilinx::xc7series::Row& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::xc7series::Row& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_ROW_H_
