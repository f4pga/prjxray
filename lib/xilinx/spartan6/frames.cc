#include <fstream>
#include <iostream>

#include <prjxray/xilinx/spartan6/frames.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

Frames::Frames2Data& Frames::getFrames() {
	return frames_data_;
}

int Frames::readFrames(const std::string& frm_file_str) {
	assert(!frm_file_str.empty());

	std::ifstream frm_file(frm_file_str);
	if (!frm_file) {
		std::cerr << "Unable to open frm file: " << frm_file_str
		          << std::endl;
		return 1;
	}
	std::string frm_line;

	while (std::getline(frm_file, frm_line)) {
		if (frm_line[0] == '#')
			continue;

		std::pair<std::string, std::string> frame_delta =
		    absl::StrSplit(frm_line, ' ');

		uint32_t frame_address =
		    std::stoul(frame_delta.first, nullptr, 16);

		std::vector<std::string> frame_data_strings =
		    absl::StrSplit(frame_delta.second, ',');

		FrameData frame_data(frame_data_strings.size(), 0);
		std::transform(frame_data_strings.begin(),
		               frame_data_strings.end(), frame_data.begin(),
		               [](const std::string& val) -> uint32_t {
			               return std::stoul(val, nullptr, 16);
		               });

		// Insert the frame address and corresponding frame data to the
		// map
		FrameAddress frm_addr(frame_address);
		frames_data_.insert(
		    std::pair<FrameAddress, FrameData>(frm_addr, frame_data));
	}
	return 0;
}

void Frames::addMissingFrames(const absl::optional<Part>& part) {
	auto current_frame_address =
	    absl::optional<FrameAddress>(FrameAddress(0));
	do {
		auto iter = frames_data_.find(*current_frame_address);
		if (iter == frames_data_.end()) {
			FrameData frame_data(65, 0);
			frames_data_.insert(std::pair<FrameAddress, FrameData>(
			    *current_frame_address, frame_data));
		}
		current_frame_address =
		    part->GetNextFrameAddress(*current_frame_address);
	} while (current_frame_address);
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray
