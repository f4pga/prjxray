#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_FRAME_ADDRESS_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_FRAME_ADDRESS_H_

#include <cstdint>

#include <prjxray/xilinx/xc7series/block_type.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class ConfigurationFrameAddress {
 public:
	ConfigurationFrameAddress()
		: address_(0) {}

	ConfigurationFrameAddress(uint32_t address)
		: address_(address) {};

	ConfigurationFrameAddress(
		BlockType block_type, bool is_bottom_half_rows,
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

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template<>
struct convert<prjxray::xilinx::xc7series::ConfigurationFrameAddress> {
	static Node encode(const prjxray::xilinx::xc7series::ConfigurationFrameAddress &rhs);
	static bool decode(const Node& node,
			   prjxray::xilinx::xc7series::ConfigurationFrameAddress &lhs);
};
} // namespace YAML
#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_FRAME_ADDRESS_H_
