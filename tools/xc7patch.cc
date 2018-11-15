#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

#include <absl/strings/str_cat.h>
#include <absl/strings/str_split.h>
#include <absl/time/clock.h>
#include <absl/time/time.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/bitstream_writer.h>
#include <prjxray/xilinx/xc7series/command.h>
#include <prjxray/xilinx/xc7series/configuration.h>
#include <prjxray/xilinx/xc7series/configuration_options_0_value.h>
#include <prjxray/xilinx/xc7series/configuration_packet_with_payload.h>
#include <prjxray/xilinx/xc7series/ecc.h>
#include <prjxray/xilinx/xc7series/nop_packet.h>
#include <prjxray/xilinx/xc7series/part.h>

DEFINE_string(part_name, "", "");
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

int patch_frames(const std::string &frm_file_str,
		std::map<xc7series::FrameAddress, std::vector<uint32_t>> *frames) {
	// Apply the deltas.
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

		auto iter = frames->find(frame_address);
		if(iter == frames->end()) {
			std::cerr
				<< "frame address 0x" << std::hex <<frame_address
				<< " because it was not found frames." << std::endl;
			return 1;
		}

		auto& frame_data = iter->second;
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

	return 0;
}

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

	if(!FLAGS_frm_file.empty()) {
		int ret = patch_frames(FLAGS_frm_file, &frames);
		if(ret != 0) {
			return ret;
		}
	}

	std::vector<std::unique_ptr<xc7series::ConfigurationPacket>>
	    out_packets;

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

	// Initialization sequence
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::TIMER, {0x0}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::WBSTAR, {0x0}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::NOP)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::UNKNOWN, {0x0}));

	// Configuration Options 0
	out_packets.emplace_back(new xc7series::ConfigurationPacketWithPayload<
	                         1>(
	    xc7series::ConfigurationPacket::Opcode::Write,
	    xc7series::ConfigurationRegister::COR0,
	    {xc7series::ConfigurationOptions0Value()
	         .SetAddPipelineStageForDoneIn(true)
	         .SetReleaseDonePinAtStartupCycle(
	             xc7series::ConfigurationOptions0Value::SignalReleaseCycle::
	                 Phase4)
	         .SetStallAtStartupCycleUntilDciMatch(
	             xc7series::ConfigurationOptions0Value::StallCycle::NoWait)
	         .SetStallAtStartupCycleUntilMmcmLock(
	             xc7series::ConfigurationOptions0Value::StallCycle::NoWait)
	         .SetReleaseGtsSignalAtStartupCycle(
	             xc7series::ConfigurationOptions0Value::SignalReleaseCycle::
	                 Phase5)
	         .SetReleaseGweSignalAtStartupCycle(
	             xc7series::ConfigurationOptions0Value::SignalReleaseCycle::
	                 Phase6)}));

	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::COR1, {0x0}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::IDCODE, {part->idcode()}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::SWITCH)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::MASK, {0x401}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CTL0, {0x501}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::MASK, {0x0}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CTL1, {0x0}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::FAR, {0x0}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::WCFG)}));
	out_packets.emplace_back(new xc7series::NopPacket());

	// Frame data write
	out_packets.emplace_back(new xc7series::ConfigurationPacket(
	    1, xc7series::ConfigurationPacket::Opcode::Write,
	    xc7series::ConfigurationRegister::FDRI, {}));
	out_packets.emplace_back(new xc7series::ConfigurationPacket(
	    2, xc7series::ConfigurationPacket::Opcode::Write,
	    xc7series::ConfigurationRegister::FDRI, packet_data));

	// Finalization sequence
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::GRESTORE)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::LFRM)}));
	for (int ii = 0; ii < 100; ++ii) {
		out_packets.emplace_back(new xc7series::NopPacket());
	}
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::START)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::FAR, {0x3be0000}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::MASK, {0x501}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CTL0, {0x501}));
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(new xc7series::NopPacket());
	out_packets.emplace_back(
	    new xc7series::ConfigurationPacketWithPayload<1>(
	        xc7series::ConfigurationPacket::Opcode::Write,
	        xc7series::ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::DESYNC)}));
	for (int ii = 0; ii < 400; ++ii) {
		out_packets.emplace_back(new xc7series::NopPacket());
	}

	// Write bitstream.
	xc7series::BitstreamWriter out_bitstream_writer(out_packets);
	std::ofstream out_file(FLAGS_output_file);
	if (!out_file) {
		std::cerr << "Unable to open file for writting: "
		          << FLAGS_output_file << std::endl;
		return 1;
	}

	// Xilinx BIT header.
	// Sync header
	std::vector<uint8_t> bit_header{0x0,  0x9,  0x0f, 0xf0, 0x0f,
	                                0xf0, 0x0f, 0xf0, 0x0f, 0xf0,
	                                0x00, 0x00, 0x01, 'a'};
	auto build_source = absl::StrCat(FLAGS_frm_file, ";Generator=xc7patch");
	bit_header.push_back(
	    static_cast<uint8_t>((build_source.size() + 1) >> 8));
	bit_header.push_back(static_cast<uint8_t>(build_source.size() + 1));
	bit_header.insert(bit_header.end(), build_source.begin(),
	                  build_source.end());
	bit_header.push_back(0x0);

	// Source file.
	bit_header.push_back('b');
	bit_header.push_back(
	    static_cast<uint8_t>((FLAGS_part_name.size() + 1) >> 8));
	bit_header.push_back(static_cast<uint8_t>(FLAGS_part_name.size() + 1));
	bit_header.insert(bit_header.end(), FLAGS_part_name.begin(),
	                  FLAGS_part_name.end());
	bit_header.push_back(0x0);

	// Build timestamp.
	auto build_time = absl::Now();
	auto build_date_string =
	    absl::FormatTime("%E4Y/%m/%d", build_time, absl::UTCTimeZone());
	auto build_time_string =
	    absl::FormatTime("%H:%M:%S", build_time, absl::UTCTimeZone());

	bit_header.push_back('c');
	bit_header.push_back(
	    static_cast<uint8_t>((build_date_string.size() + 1) >> 8));
	bit_header.push_back(
	    static_cast<uint8_t>(build_date_string.size() + 1));
	bit_header.insert(bit_header.end(), build_date_string.begin(),
	                  build_date_string.end());
	bit_header.push_back(0x0);

	bit_header.push_back('d');
	bit_header.push_back(
	    static_cast<uint8_t>((build_time_string.size() + 1) >> 8));
	bit_header.push_back(
	    static_cast<uint8_t>(build_time_string.size() + 1));
	bit_header.insert(bit_header.end(), build_time_string.begin(),
	                  build_time_string.end());
	bit_header.push_back(0x0);

	bit_header.insert(bit_header.end(), {'e', 0x0, 0x0, 0x0, 0x0});
	out_file.write(reinterpret_cast<const char*>(bit_header.data()),
	               bit_header.size());

	auto end_of_header_pos = out_file.tellp();
	auto header_data_length_pos =
	    end_of_header_pos - static_cast<std::ofstream::off_type>(4);

	for (uint32_t word : out_bitstream_writer) {
		out_file.put((word >> 24) & 0xFF);
		out_file.put((word >> 16) & 0xFF);
		out_file.put((word >> 8) & 0xFF);
		out_file.put((word)&0xFF);
	}

	uint32_t length_of_data = out_file.tellp() - end_of_header_pos;

	out_file.seekp(header_data_length_pos);
	out_file.put((length_of_data >> 24) & 0xFF);
	out_file.put((length_of_data >> 16) & 0xFF);
	out_file.put((length_of_data >> 8) & 0xFF);
	out_file.put((length_of_data)&0xFF);

	return 0;
}
