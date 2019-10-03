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

		FrameData frame_data(frame_data_strings.size(), 0);
		std::transform(frame_data_strings.begin(),
		               frame_data_strings.end(), frame_data.begin(),
		               [](const std::string& val) -> uint32_t {
			               return std::stoul(val, nullptr, 16);
		               });

		// Spartan6 doesn't have ECC
		if (!std::is_same_v<ArchType, Spartan6>) {
			updateECC(frame_data);
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

uint32_t calculateECC(const typename Frames<Series7>::FrameData& data) {
	uint32_t ecc = 0;
	for (size_t ii = 0; ii < data.size(); ++ii) {
		ecc = xc7series::icap_ecc(ii, data[ii], ecc);
	}
	return ecc;
}

template <>
void Frames<Series7>::updateECC(FrameData& data) {
	assert(data.size() != 0);
	// Replace the old ECC with the new.
	data[0x32] &= 0xFFFFE000;
	data[0x32] |= (calculateECC(data) & 0x1FFF);
}

template Frames<Spartan6>::Frames2Data& Frames<Spartan6>::getFrames();
template Frames<Series7>::Frames2Data& Frames<Series7>::getFrames();
template void Frames<Spartan6>::addMissingFrames(
    const absl::optional<Spartan6::Part>& part);
template void Frames<Series7>::addMissingFrames(
    const absl::optional<Series7::Part>& part);
template int Frames<Spartan6>::readFrames(const std::string&);
template int Frames<Series7>::readFrames(const std::string&);
template void Frames<Series7>::updateECC(Frames<Series7>::FrameData&);

}  // namespace xilinx
}  // namespace prjxray
