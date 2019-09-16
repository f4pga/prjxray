#include <prjxray/xilinx/spartan6/row.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

bool Row::IsValidFrameAddress(FrameAddress address) const {
	auto addr_bus = configuration_buses_.find(address.block_type());
	if (addr_bus == configuration_buses_.end())
		return false;
	return addr_bus->second.IsValidFrameAddress(address);
}

absl::optional<FrameAddress> Row::GetNextFrameAddress(
    FrameAddress address) const {
	// Find the bus for the current address.
	auto addr_bus = configuration_buses_.find(address.block_type());

	// If the current address isn't in a known bus, no way to know the next.
	if (addr_bus == configuration_buses_.end())
		return {};

	// Ask the bus for the next address.
	absl::optional<FrameAddress> next_address =
	    addr_bus->second.GetNextFrameAddress(address);
	if (next_address)
		return next_address;

	// The current bus doesn't know what the next address is. Rows come next
	// in frame address numerical order so punt back to the caller to figure
	// it out.
	return {};
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace spartan6 = prjxray::xilinx::spartan6;

namespace YAML {

Node convert<spartan6::Row>::encode(const spartan6::Row& rhs) {
	Node node;
	node.SetTag("xilinx/spartan6/row");
	node["configuration_buses"] = rhs.configuration_buses_;
	return node;
}

bool convert<spartan6::Row>::decode(const Node& node, spartan6::Row& lhs) {
	if (!node.Tag().empty() && node.Tag() != "xilinx/spartan6/row") {
		return false;
	}

	lhs.configuration_buses_ =
	    node["configuration_buses"]
	        .as<std::map<spartan6::BlockType,
	                     spartan6::ConfigurationBus>>();
	return true;
}

}  // namespace YAML
