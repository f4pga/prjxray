#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_FRAME_RANGE_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_FRAME_RANGE_H_

#include <cstdint>

#include <prjxray/xilinx/xc7series/frame_address.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class ConfigurationFrameRange {
       public:
	ConfigurationFrameRange() : begin_(0), end_(0) {}

	ConfigurationFrameRange(FrameAddress begin, FrameAddress end)
	    : begin_(begin), end_(end){};

	FrameAddress begin() const { return begin_; }
	FrameAddress end() const { return end_; }

	size_t size() const { return end_ - begin_; }
	bool empty() const { return size() == 0; }

	bool Contains(FrameAddress address) const;

       private:
	FrameAddress begin_;
	FrameAddress end_;
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::xc7series::ConfigurationFrameRange> {
	static Node encode(
	    const prjxray::xilinx::xc7series::ConfigurationFrameRange& rhs);
	static bool decode(
	    const Node& node,
	    prjxray::xilinx::xc7series::ConfigurationFrameRange& lhs);
};
}  // namespace YAML
#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_FRAME_RANGE_H_
