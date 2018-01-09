#include <prjxray/xilinx/xc7series/configuration_frame_range.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

bool ConfigurationFrameRange::Contains(FrameAddress address) const {
	return address >= begin_ && address < end_;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace xc7series = prjxray::xilinx::xc7series;

namespace YAML {

Node convert<xc7series::ConfigurationFrameRange>::encode(
    const xc7series::ConfigurationFrameRange& rhs) {
	Node node;
	node.SetTag("xilinx/xc7series/configuration_frame_range");
	node["begin"] = rhs.begin();
	node["end"] = rhs.end();
	return node;
}

bool convert<xc7series::ConfigurationFrameRange>::decode(
    const Node& node,
    xc7series::ConfigurationFrameRange& lhs) {
	if (node.Tag() != "xilinx/xc7series/configuration_frame_range" ||
	    !node["begin"] || !node["end"])
		return false;

	lhs = xc7series::ConfigurationFrameRange(
	    node["begin"].as<xc7series::FrameAddress>(),
	    node["end"].as<xc7series::FrameAddress>());
	return true;
}

}  // namespace YAML
