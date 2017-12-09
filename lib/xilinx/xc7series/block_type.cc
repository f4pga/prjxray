#include <prjxray/xilinx/xc7series/block_type.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

std::ostream &operator<<(std::ostream &o, BlockType value) {
	switch (value) {
	case BlockType::CLB_IO_CLK:
		o << "CLB/IO/CLK";
		break;
	case BlockType::BLOCK_RAM:
		o << "Block RAM";
		break;
	case BlockType::CFG_CLB:
		o << "Config CLB";
		break;
	}

	return o;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
