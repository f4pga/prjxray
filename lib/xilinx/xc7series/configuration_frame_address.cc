#include <prjxray/xilinx/xc7series/configuration_frame_address.h>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

BlockType ConfigurationFrameAddress::block_type() const {
	return static_cast<BlockType>(bit_field_get(address_, 25, 23));
}

bool ConfigurationFrameAddress::is_bottom_half_rows() const {
	return bit_field_get(address_, 22, 22);
}

uint8_t ConfigurationFrameAddress::row_address() const {
	return bit_field_get(address_, 21, 17);
}

uint16_t ConfigurationFrameAddress::column_address() const {
	return bit_field_get(address_, 16, 7);
}

uint8_t ConfigurationFrameAddress::minor_address() const {
	return bit_field_get(address_, 6, 0);
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
