#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_FRAME_ADDRESS_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_FRAME_ADDRESS_H_

#include <cstdint>
#include <ostream>

#include <prjxray/xilinx/spartan6/block_type.h>
#include <yaml-cpp/yaml.h>

#ifdef _GNU_SOURCE
#undef minor
#endif

namespace prjxray {
namespace xilinx {
namespace spartan6 {
class FrameAddress {
       public:
	FrameAddress() : address_(0) {}

	FrameAddress(uint32_t address) : address_(address){};

	FrameAddress(BlockType block_type,
	             uint8_t row,
	             uint8_t column,
	             uint16_t minor);

	operator uint32_t() const { return address_; }
	bool is_bottom_half_rows() const;
	BlockType block_type() const;
	uint8_t row() const;
	uint8_t column() const;
	uint16_t minor() const;

       private:
	uint32_t address_;
};

std::ostream& operator<<(std::ostream& o, const FrameAddress& addr);

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::spartan6::FrameAddress> {
	static Node encode(const prjxray::xilinx::spartan6::FrameAddress& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::spartan6::FrameAddress& lhs);
};
}  // namespace YAML
#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_FRAME_ADDRESS_H_
