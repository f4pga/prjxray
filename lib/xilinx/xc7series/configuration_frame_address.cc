#include <prjxray/xilinx/xc7series/configuration_frame_address.h>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {


ConfigurationFrameAddress::ConfigurationFrameAddress(
	BlockType block_type, bool is_bottom_half_rows,
	uint8_t row, uint16_t column, uint8_t minor) {
	address_ = bit_field_set(0, 25, 23, block_type);
	address_ = bit_field_set(address_, 22, 22, is_bottom_half_rows);
	address_ = bit_field_set(address_, 21, 17, row);
	address_ = bit_field_set(address_, 16, 7, column);
	address_ = bit_field_set(address_, 6, 0, minor);
}

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

namespace YAML {

namespace xc7series = prjxray::xilinx::xc7series;

Node convert<xc7series::ConfigurationFrameAddress>::encode(
		const xc7series::ConfigurationFrameAddress &rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/configuration_frame_address");
	node["block_type"] = rhs.block_type();
	node["row_half"] = (rhs.is_bottom_half_rows() ? "bottom" : "top");
	node["row"] = static_cast<unsigned int>(rhs.row_address());
	node["column"] = static_cast<unsigned int>(rhs.column_address());
	node["minor"] = static_cast<unsigned int>(rhs.minor_address());
	return node;
}

bool convert<xc7series::ConfigurationFrameAddress>::decode(
		const Node &node, xc7series::ConfigurationFrameAddress &lhs) {
	if (node.Tag() != "xilinx/xc7series/configuration_frame_address" ||
	    !node["block_type"] ||
	    !node["row_half"] ||
	    !node["row"] ||
	    !node["column"] ||
	    !node["minor"]) return false;

	bool row_half;
	if (node["row_half"].as<std::string>() == "top") {
		row_half = false;
	} else if (node["row_half"].as<std::string>() == "bottom") {
		row_half = true;
	} else {
		return false;
	}

	lhs = prjxray::xilinx::xc7series::ConfigurationFrameAddress(
			node["block_type"].as<xc7series::BlockType>(),
			row_half,
			node["row"].as<unsigned int>(),
			node["column"].as<unsigned int>(),
			node["minor"].as<unsigned int>());
	return true;
}

}  // namespace YAML;
