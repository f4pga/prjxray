#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_

#include <ostream>

namespace prjxray {
namespace xilinx {
namespace xc7series {

enum class BlockType : unsigned int {
	CLB_IO_CLK = 0x0,
	BLOCK_RAM = 0x1,
	CFG_CLB = 0x2,
	/* reserved = 0x3, */
};

std::ostream &operator<<(std::ostream &o, BlockType value);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_
