#ifndef PRJXRAY_LIB_XILINX_FRAMES_H
#define PRJXRAY_LIB_XILINX_FRAMES_H

#include <map>
#include <string>
#include <vector>

#include <prjxray/xilinx/architectures.h>

namespace prjxray {
namespace xilinx {

// Contains frame information which is used for the generation
// of the configuration package that is used in bitstream generation.
template <typename ArchType>
class Frames {
       public:
	typedef std::vector<uint32_t> FrameData;
	typedef std::map<typename ArchType::FrameAddress, FrameData>
	    Frames2Data;

	// Reads the contents of the frames file and populates
	// the Frames container.
	int readFrames(const std::string& frm_file_str);

	// Adds empty frames that are present in the tilegrid of a specific part
	// but are missing in the current frames container.
	void addMissingFrames(
	    const absl::optional<typename ArchType::Part>& part);

	// Returns the map with frame addresses and corresponding data
	Frames2Data& getFrames();

       private:
	Frames2Data frames_data_;

	// Updates the ECC information in the frame.
	void updateECC(FrameData& data);
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_FRAMES_H
