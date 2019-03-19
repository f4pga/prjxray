#include <fstream>
#include <iostream>

#include <absl/strings/str_cat.h>
#include <absl/strings/str_split.h>
#include <absl/time/clock.h>
#include <absl/time/time.h>
//#include <gflags/gflags.h>

#include <prjxray/xilinx/xc7series/bitstream_writer.h>
#include <prjxray/xilinx/xc7series/command.h>
#include <prjxray/xilinx/xc7series/configuration_options_0_value.h>
#include <prjxray/xilinx/xc7series/configuration_packet_with_payload.h>
#include <prjxray/xilinx/xc7series/nop_packet.h>
#include <prjxray/xilinx/xc7series/utils.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

PacketData createType2ConfigurationPacketData(const Frames::Frames2Data& frames,
                                              absl::optional<Part>& part) {
	// Generate a single type 2 packet that writes everything at once.
	PacketData packet_data;
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
	return packet_data;
}

void createConfigurationPackage(ConfigurationPackage& out_packets,
                                const PacketData& packet_data,
                                absl::optional<Part>& part) {
	// Initialization sequence
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::TIMER,
	    {0x0}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::WBSTAR,
	    {0x0}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::NOP)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::RCRC)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::UNKNOWN,
	    {0x0}));

	// Configuration Options 0
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::COR0,
	    {ConfigurationOptions0Value()
	         .SetAddPipelineStageForDoneIn(true)
	         .SetReleaseDonePinAtStartupCycle(
	             ConfigurationOptions0Value::SignalReleaseCycle::Phase4)
	         .SetStallAtStartupCycleUntilDciMatch(
	             ConfigurationOptions0Value::StallCycle::NoWait)
	         .SetStallAtStartupCycleUntilMmcmLock(
	             ConfigurationOptions0Value::StallCycle::NoWait)
	         .SetReleaseGtsSignalAtStartupCycle(
	             ConfigurationOptions0Value::SignalReleaseCycle::Phase5)
	         .SetReleaseGweSignalAtStartupCycle(
	             ConfigurationOptions0Value::SignalReleaseCycle::Phase6)}));

	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::COR1,
	    {0x0}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::IDCODE,
	    {part->idcode()}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::SWITCH)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::MASK,
	    {0x401}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CTL0,
	    {0x501}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::MASK,
	    {0x0}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CTL1,
	    {0x0}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::FAR,
	    {0x0}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::WCFG)}));
	out_packets.emplace_back(new NopPacket());

	// Frame data write
	out_packets.emplace_back(
	    new ConfigurationPacket(1, ConfigurationPacket::Opcode::Write,
	                            ConfigurationRegister::FDRI, {}));
	out_packets.emplace_back(
	    new ConfigurationPacket(2, ConfigurationPacket::Opcode::Write,
	                            ConfigurationRegister::FDRI, packet_data));

	// Finalization sequence
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::RCRC)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::GRESTORE)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::LFRM)}));
	for (int ii = 0; ii < 100; ++ii) {
		out_packets.emplace_back(new NopPacket());
	}
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::START)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::FAR,
	    {0x3be0000}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::MASK,
	    {0x501}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CTL0,
	    {0x501}));
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::RCRC)}));
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::DESYNC)}));
	for (int ii = 0; ii < 400; ++ii) {
		out_packets.emplace_back(new NopPacket());
	}
}

BitstreamHeader createBitstreamHeader(const std::string& part_name,
                                      const std::string& frames_file_name,
                                      const std::string& generator_name) {
	// Sync header
	BitstreamHeader bit_header{0x0,  0x9,  0x0f, 0xf0, 0x0f, 0xf0, 0x0f,
	                           0xf0, 0x0f, 0xf0, 0x00, 0x00, 0x01, 'a'};
	auto build_source =
	    absl::StrCat(frames_file_name, ";Generator=" + generator_name);
	bit_header.push_back(
	    static_cast<uint8_t>((build_source.size() + 1) >> 8));
	bit_header.push_back(static_cast<uint8_t>(build_source.size() + 1));
	bit_header.insert(bit_header.end(), build_source.begin(),
	                  build_source.end());
	bit_header.push_back(0x0);

	// Source file.
	bit_header.push_back('b');
	bit_header.push_back(static_cast<uint8_t>((part_name.size() + 1) >> 8));
	bit_header.push_back(static_cast<uint8_t>(part_name.size() + 1));
	bit_header.insert(bit_header.end(), part_name.begin(), part_name.end());
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

	return bit_header;
}

int writeBitstream(const ConfigurationPackage& packets,
                   const std::string& part_name,
                   const std::string& frames_file,
                   const std::string& generator_name,
                   const std::string& output_file) {
	std::ofstream out_file(output_file, std::ofstream::binary);
	if (!out_file) {
		std::cerr << "Unable to open file for writting: " << output_file
		          << std::endl;
		return 1;
	}

	BitstreamHeader bit_header(
	    createBitstreamHeader(part_name, frames_file, generator_name));
	out_file.write(reinterpret_cast<const char*>(bit_header.data()),
	               bit_header.size());

	auto end_of_header_pos = out_file.tellp();
	auto header_data_length_pos =
	    end_of_header_pos - static_cast<std::ofstream::off_type>(4);

	BitstreamWriter out_bitstream_writer(packets);
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

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
