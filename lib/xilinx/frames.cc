#include <fstream>
#include <iostream>

#include <absl/strings/str_split.h>

#include <prjxray/xilinx/frames.h>
#include <prjxray/xilinx/xc7series/ecc.h>

namespace prjxray {
namespace xilinx {

template <typename ArchType>
typename Frames<ArchType>::Frames2Data& Frames<ArchType>::getFrames() {
	return frames_data_;
}

template <typename ArchType>
int Frames<ArchType>::readFrames(const std::string& frm_file_str) {
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

		if (frame_data_strings.size() != ArchType::words_per_frame) {
			std::cerr << "Frame " << std::hex << frame_address
			          << ": found " << std::dec
			          << frame_data_strings.size()
			          << " words instead of "
			          << ArchType::words_per_frame << std::endl;
			continue;
		}

		FrameData frame_data(frame_data_strings.size(), 0);
		std::transform(frame_data_strings.begin(),
		               frame_data_strings.end(), frame_data.begin(),
		               [](const std::string& val) -> uint32_t {
			               return std::stoul(val, nullptr, 16);
		               });

		// Spartan6 doesn't have ECC
		if (std::is_same<ArchType, Series7>::value) {
			xc7series::updateECC(frame_data);
		}

		// Insert the frame address and corresponding frame data to the
		// map
		typename ArchType::FrameAddress frm_addr(frame_address);
		frames_data_.insert(
		    std::pair<typename ArchType::FrameAddress, FrameData>(
		        frm_addr, frame_data));
	}
	return 0;
}

template <typename ArchType>
void Frames<ArchType>::addMissingFrames(
    const absl::optional<typename ArchType::Part>& part) {
	auto current_frame_address =
	    absl::optional<typename ArchType::FrameAddress>(
	        typename ArchType::FrameAddress(0));
	do {
		auto iter = frames_data_.find(*current_frame_address);
		if (iter == frames_data_.end()) {
			FrameData frame_data(ArchType::words_per_frame, 0);
			frames_data_.insert(
			    std::pair<typename ArchType::FrameAddress,
			              FrameData>(*current_frame_address,
			                         frame_data));
		}
		current_frame_address =
		    part->GetNextFrameAddress(*current_frame_address);
	} while (current_frame_address);
}

template Frames<Series7>::Frames2Data& Frames<Series7>::getFrames();
template void Frames<Series7>::addMissingFrames(
    const absl::optional<Series7::Part>& part);
template int Frames<Series7>::readFrames(const std::string&);

}  // namespace xilinx
}  // namespace prjxray
