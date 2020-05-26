/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_

#include <ostream>

#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

enum class BlockType : unsigned int {
	CLB_IO_CLK = 0x0,
	BLOCK_RAM = 0x1,
	CFG_CLB = 0x2,
	/* reserved = 0x3, */
};

std::ostream& operator<<(std::ostream& o, BlockType value);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::xc7series::BlockType> {
	static Node encode(const prjxray::xilinx::xc7series::BlockType& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::xc7series::BlockType& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_
