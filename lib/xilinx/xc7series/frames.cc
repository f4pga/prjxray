#include <fstream>
#include <iostream>

#include <prjxray/xilinx/xc7series/ecc.h>
#include <prjxray/xilinx/xc7series/frames.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

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
		if (frame_data_strings.size() != 101) {
			std::cerr << "Frame " << std::hex << frame_address
			          << ": found " << std::dec
			          << frame_data_strings.size()
			          << "words instead of 101";
			continue;
		}

		FrameData frame_data(101, 0);
		std::transform(frame_data_strings.begin(),
		               frame_data_strings.end(), frame_data.begin(),
		               [](const std::string& val) -> uint32_t {
			               return std::stoul(val, nullptr, 16);
		               });

		// TODO make sure if this is needed
		updateECC(frame_data);

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
			FrameData frame_data(101, 0);
			// TODO make sure if this is needed
			updateECC(frame_data);
			frames_data_.insert(std::pair<FrameAddress, FrameData>(
			    *current_frame_address, frame_data));
		}
		current_frame_address =
		    part->GetNextFrameAddress(*current_frame_address);
	} while (current_frame_address);
}

void Frames::updateECC(FrameData& data) {
	assert(data.size() != 0);
	// Replace the old ECC with the new.
	data[0x32] &= 0xFFFFE000;
	data[0x32] |= (calculateECC(data) & 0x1FFF);
}

uint32_t Frames::calculateECC(const FrameData& data) {
	uint32_t ecc = 0;
	for (size_t ii = 0; ii < data.size(); ++ii) {
		ecc = icap_ecc(ii, data[ii], ecc);
	}
	return ecc;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
