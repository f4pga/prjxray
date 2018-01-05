#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_

#include <vector>

#include <absl/types/optional.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <prjxray/xilinx/xc7series/configuration_frame_range.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class Part {
 public:
	static absl::optional<Part> FromFile(const std::string &path);

	// Constructs an invalid part with a zero IDCODE. Required for YAML
	// conversion but shouldn't be used otherwise.
	Part() : idcode_(0), frame_ranges_() {}

	Part(uint32_t idcode,
	     const std::vector<ConfigurationFrameRange> &ranges)
	: idcode_(idcode), frame_ranges_(std::move(ranges)) {}

	uint32_t idcode() const { return idcode_; }

	const std::vector<ConfigurationFrameRange>&
	configuration_frame_ranges() const { return frame_ranges_; }

	absl::optional<FrameAddress>
	GetNextFrameAddress(FrameAddress address) const;

 private:
  uint32_t idcode_;

  // Ranges are expected to be non-overlapping.
  std::vector<ConfigurationFrameRange> frame_ranges_;
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template<>
struct convert<prjxray::xilinx::xc7series::Part> {
	static Node encode(const prjxray::xilinx::xc7series::Part &rhs);
	static bool decode(const Node& node,
			   prjxray::xilinx::xc7series::Part &lhs);
};
} // namespace YAML

#endif // PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_
