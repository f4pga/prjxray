#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H

#include <string>
#include <vector>

#include <absl/strings/str_split.h>
#include <prjxray/xilinx/spartan6/configuration.h>
#include <prjxray/xilinx/spartan6/frame_address.h>
#include <prjxray/xilinx/spartan6/part.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

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
};

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_FRAMES_H
