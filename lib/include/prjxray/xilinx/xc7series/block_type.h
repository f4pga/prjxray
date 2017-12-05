#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_

namespace prjxray {
namespace xilinx {
namespace xc7series {

enum class BlockType : unsigned int {
	CLB_IO_CLK = 0b000,
	BLOCK_RAM = 0b001,
	CFG_CLB = 0b010,
	/* reserved = 0b011, */
};
	
}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_BLOCK_TYPE_H_
