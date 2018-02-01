#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

#include <absl/strings/str_split.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/bitstream_writer.h>
#include <prjxray/xilinx/xc7series/configuration.h>
#include <prjxray/xilinx/xc7series/ecc.h>
#include <prjxray/xilinx/xc7series/part.h>

DEFINE_string(part_file, "", "Definition file for target 7-series part");
DEFINE_string(bitstream_file,
              "",
              "Initial bitstream to which the deltas are applied.");
DEFINE_string(
    frm_file,
    "",
    "File containing a list of frame deltas to be applied to the base "
    "bitstream.  Each line in the file is of the form: "
    "<frame_address> <word1>,...,<word101>.");
DEFINE_string(output_file, "", "Write patched bitsteam to file");

namespace xc7series = prjxray::xilinx::xc7series;

int main(int argc, char* argv[]) {
	gflags::SetUsageMessage(argv[0]);
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	auto part = xc7series::Part::FromFile(FLAGS_part_file);
	if (!part) {
		std::cerr << "Part file not found or invalid" << std::endl;
		return 1;
	}

	auto bitstream_file =
	    prjxray::MemoryMappedFile::InitWithFile(FLAGS_bitstream_file);
	if (!bitstream_file) {
		std::cerr << "Can't open base bitstream file: "
		          << FLAGS_bitstream_file << std::endl;
		return 1;
	}

	auto bitstream_reader = xc7series::BitstreamReader::InitWithBytes(
	    bitstream_file->as_bytes());
	if (!bitstream_reader) {
		std::cout
		    << "Bitstream does not appear to be a 7-series bitstream!"
		    << std::endl;
		return 1;
	}

	auto bitstream_config =
	    xc7series::Configuration::InitWithPackets(*part, *bitstream_reader);
	if (!bitstream_config) {
		std::cerr << "Bitstream does not appear to be for this part"
		          << std::endl;
		return 1;
	}

	// Copy the base frames to a mutable collection
	std::map<xc7series::FrameAddress, std::vector<uint32_t>> frames;
	for (auto& frame_val : bitstream_config->frames()) {
		auto& cur_frame = frames[frame_val.first];

		std::copy(frame_val.second.begin(), frame_val.second.end(),
		          std::back_inserter(cur_frame));
	}

	// Apply the deltas.
	std::ifstream frm_file(FLAGS_frm_file);
	if (!frm_file) {
		std::cerr << "Unable to open frm file: " << FLAGS_frm_file
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

		auto& frame_data = frames[frame_address];
		frame_data.resize(101);

		std::vector<std::string> frame_data_strings =
		    absl::StrSplit(frame_delta.second, ',');
		if (frame_data_strings.size() != 101) {
			std::cerr << "Frame " << std::hex << frame_address
			          << ": found " << std::dec
			          << frame_data_strings.size()
			          << "words instead of 101";
			continue;
		};

		std::transform(frame_data_strings.begin(),
		               frame_data_strings.end(), frame_data.begin(),
		               [](const std::string& val) -> uint32_t {
			               return std::stoul(val, nullptr, 16);
		               });

		uint32_t ecc = 0;
		for (size_t ii = 0; ii < frame_data.size(); ++ii) {
			ecc = xc7series::icap_ecc(ii, frame_data[ii], ecc);
		}

		// Replace the old ECC with the new.
		frame_data[0x32] &= 0xFFFFE000;
		frame_data[0x32] |= (ecc & 0x1FFF);
	}

#if 0
	for (auto& frame : frames) {
		std::cout << "0x" << std::hex
		          << static_cast<uint32_t>(frame.first) << " ";

		for (auto& word : frame.second) {
			std::cout << "0x" << std::hex << word << ",";
		}

		std::cout << std::endl;
	}
#endif
	std::vector<xc7series::ConfigurationPacket> out_packets;

	// Generate a single type 2 packet that writes everything at once.
	std::vector<uint32_t> packet_data;
	for (auto& frame : frames) {
		std::copy(frame.second.begin(), frame.second.end(),
		          std::back_inserter(packet_data));

		auto next_address = part->GetNextFrameAddress(frame.first);
		if (next_address &&
		    (next_address->block_type() != frame.first.block_type() ||
		     next_address->is_bottom_half_rows() !=
		         frame.first.is_bottom_half_rows() ||
		     next_address->row() != frame.first.row())) {
			packet_data.insert(packet_data.end(), 202, 0);
		}
	}
	packet_data.insert(packet_data.end(), 202, 0);

	out_packets.push_back(xc7series::ConfigurationPacket(
	    1, xc7series::ConfigurationPacket::Opcode::Write,
	    xc7series::ConfigurationRegister::FDRI, {}));
	out_packets.push_back(xc7series::ConfigurationPacket(
	    2, xc7series::ConfigurationPacket::Opcode::Write,
	    xc7series::ConfigurationRegister::FDRI, packet_data));

#if 0
	for (auto& packet : out_packets) {
		std::cout << packet << std::endl;
	}
#endif

	// Write bitstream.
	xc7series::BitstreamWriter out_bitstream_writer(out_packets);
	std::ofstream out_file(FLAGS_output_file);
	if (!out_file) {
		std::cerr << "Unable to open file for writting: "
		          << FLAGS_output_file << std::endl;
		return 1;
	}

	for (uint32_t word : out_bitstream_writer) {
		out_file.put((word >> 24) & 0xFF);
		out_file.put((word >> 16) & 0xFF);
		out_file.put((word >> 8) & 0xFF);
		out_file.put((word)&0xFF);
	}

	return 0;
}
