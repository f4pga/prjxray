#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_

#include <algorithm>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include <absl/types/optional.h>
#include <prjxray/xilinx/spartan6/global_clock_region.h>
#include <yaml-cpp/yaml.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

class Part {
       public:
	constexpr static uint32_t kInvalidIdcode = 0;

	static absl::optional<Part> FromFile(const std::string& path);

	// Constructs an invalid part with a zero IDCODE. Required for YAML
	// conversion but shouldn't be used otherwise.
	Part() : idcode_(kInvalidIdcode) {}

	template <typename T>
	Part(uint32_t idcode, T collection)
	    : Part(idcode, std::begin(collection), std::end(collection)) {}

	template <typename T>
	Part(uint32_t idcode, T first, T last);

	uint32_t idcode() const { return idcode_; }

	bool IsValidFrameAddress(FrameAddress address) const;

	absl::optional<FrameAddress> GetNextFrameAddress(
	    FrameAddress address) const;

       private:
	friend struct YAML::convert<Part>;

	uint32_t idcode_;
	GlobalClockRegion top_region_;
	GlobalClockRegion bottom_region_;
};

template <typename T>
Part::Part(uint32_t idcode, T first, T last) : idcode_(idcode) {
	top_region_ = GlobalClockRegion(first, last);
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

namespace YAML {
template <>
struct convert<prjxray::xilinx::spartan6::Part> {
	static Node encode(const prjxray::xilinx::spartan6::Part& rhs);
	static bool decode(const Node& node,
	                   prjxray::xilinx::spartan6::Part& lhs);
};
}  // namespace YAML

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_PART_H_
