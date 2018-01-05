#include <prjxray/xilinx/xc7series/part.h>

#include <iomanip>
#include <sstream>

namespace prjxray {
namespace xilinx {
namespace xc7series {

absl::optional<Part> Part::FromFile(const std::string &path) {
	try {
		YAML::Node yaml = YAML::LoadFile(path);
		return yaml.as<Part>();
	} catch (YAML::Exception e) {
		return {};
	}
}

absl::optional<FrameAddress>
Part::GetNextFrameAddress(FrameAddress address) const {
	// Start with the next linear address.
	FrameAddress target_address(address + 1);

	// The address space is non-continguous.  If the next linear address
	// happens to fall in a valid range, that's the next address.
	// Otherwise, find the closest valid range and use it's beginning
	// address.
	absl::optional<FrameAddress> closest_address;
	int32_t closest_distance;
	for (auto iter = frame_ranges_.begin();
	     iter != frame_ranges_.end();
	     ++iter) {
		if (iter->Contains(target_address)) {
			return target_address;
		}

		int32_t distance = iter->begin() - target_address;
		if (distance > 0 &&
		    (!closest_address ||
		     distance < closest_distance)) {
			closest_address = iter->begin();
			closest_distance = distance;
		}
	}

	return closest_address;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::Part>::encode(const xc7series::Part &rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/part");

	std::ostringstream idcode_str;
	idcode_str << "0x" << std::hex << rhs.idcode();
	node["idcode"] = idcode_str.str();

	node["configuration_ranges"] = rhs.configuration_frame_ranges();
	return node;
}

bool convert<xc7series::Part>::decode(const Node &node, xc7series::Part &lhs) {
	if (node.Tag() != "xilinx/xc7series/part" ||
	    !node["idcode"] ||
	    !node["configuration_ranges"]) return false;

	lhs = xc7series::Part(
		node["idcode"].as<uint32_t>(),
		node["configuration_ranges"].as<
			std::vector<xc7series::ConfigurationFrameRange>>());
	return true;
}

}  // namespace YAML;

