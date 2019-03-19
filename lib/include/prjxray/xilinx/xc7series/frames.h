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

// Contains frame information which is used for the generation
// of the configuration package that is used in bitstream generation.
class Frames {
       public:
	typedef std::vector<uint32_t> FrameData;
	typedef std::map<FrameAddress, FrameData> Frames2Data;

	// Reads the contents of the frames file and populates
	// the Frames container.
	int readFrames(const std::string& frm_file_str);

	// Adds empty frames that are present in the tilegrid of a specific part
	// but are missing in the current frames container.
	void addMissingFrames(const absl::optional<Part>& part);

	// Returns the map with frame addresses and corresponding data
	Frames2Data& getFrames();

       private:
	Frames2Data frames_data_;

	// Updates the ECC information in the frame.
	void updateECC(FrameData& data);
	uint32_t calculateECC(const FrameData& data);
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H
