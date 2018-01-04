#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_FRAME_ADDRESS_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_FRAME_ADDRESS_H_

#include <cstdint>
#include <ostream>

#include <prjxray/xilinx/xc7series/block_type.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class FrameAddress {
 public:
	FrameAddress() : address_(0) {}

	FrameAddress(uint32_t address)
		: address_(address) {};

	FrameAddress(BlockType block_type, bool is_bottom_half_rows,
		     uint8_t row, uint16_t column, uint8_t minor);

	operator uint32_t() const { return address_; }

	BlockType block_type() const;
	bool is_bottom_half_rows() const;
	uint8_t row_address() const;
	uint16_t column_address() const;
	uint8_t minor_address() const;

 private:
	uint32_t address_;
};

std::ostream &operator<<(std::ostream &o, const FrameAddress& addr);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template<>
struct convert<prjxray::xilinx::xc7series::FrameAddress> {
	static Node encode(const prjxray::xilinx::xc7series::FrameAddress &rhs);
	static bool decode(const Node& node,
			   prjxray::xilinx::xc7series::FrameAddress &lhs);
};
} // namespace YAML
#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_FRAME_ADDRESS_H_
