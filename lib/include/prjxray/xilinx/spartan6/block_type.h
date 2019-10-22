#ifndef PRJXRAY_LIB_XILINX_SPARTAN6_BLOCK_TYPE_H_
#define PRJXRAY_LIB_XILINX_SPARTAN6_BLOCK_TYPE_H_

#include <ostream>

#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

// According to UG380 pg. 97 there are 3 types of configuration frames:
// Type 0: Core: CLB, DSP, input/output interconnect (IOI), clocking
// Type 1: Block RAM
// Type 2: IOB
enum class BlockType : unsigned int {
	CLB_IOI_CLK = 0x0,
	BLOCK_RAM = 0x1,
	IOB = 0x2,
};

std::ostream& operator<<(std::ostream& o, BlockType value);

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::spartan6::BlockType> {
	static Node encode(const prjxray::xilinx::spartan6::BlockType& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::spartan6::BlockType& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_SPARTAN6_BLOCK_TYPE_H_
