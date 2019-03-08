#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H

#include <string>
#include <vector>

#include <absl/strings/str_split.h>
#include <prjxray/xilinx/xc7series/configuration.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <prjxray/xilinx/xc7series/part.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {
class Frames {
       public:
	typedef std::vector<uint32_t> FrameData;
	typedef std::map<FrameAddress, FrameData> Frames2Data;

	int readFrames(const std::string& frm_file_str);
	void addMissingFrames(const absl::optional<Part>& part);
	Frames2Data& getFrames();

       private:
	Frames2Data frames_data_;

	void updateECC(FrameData& data);
	uint32_t calculateECC(const FrameData& data);
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H
