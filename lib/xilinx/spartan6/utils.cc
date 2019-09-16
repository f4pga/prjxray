#include <fstream>
#include <iostream>

#include <absl/strings/str_cat.h>
#include <absl/strings/str_split.h>
#include <absl/time/clock.h>
#include <absl/time/time.h>

#include <prjxray/xilinx/spartan6/bitstream_writer.h>
#include <prjxray/xilinx/spartan6/command.h>
#include <prjxray/xilinx/spartan6/configuration_options_0_value.h>
#include <prjxray/xilinx/spartan6/configuration_packet_with_payload.h>
#include <prjxray/xilinx/spartan6/nop_packet.h>
#include <prjxray/xilinx/spartan6/utils.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

PacketData createType2ConfigurationPacketData(const Frames::Frames2Data& frames,
                                              absl::optional<Part>& part) {
	// Generate a single type 2 packet that writes everything at once.
	PacketData packet_data;
	for (auto& frame : frames) {
		std::copy(frame.second.begin(), frame.second.end(),
		          std::back_inserter(packet_data));
	}

	// Insert payload length
	size_t packet_data_size = packet_data.size() - 2;
	packet_data.insert(packet_data.begin(), packet_data_size & 0xFFFF);
	packet_data.insert(packet_data.begin(),
	                   (packet_data_size >> 16) & 0xFFFF);
	return packet_data;
}

void createConfigurationPackage(ConfigurationPackage& out_packets,
                                const PacketData& packet_data,
                                absl::optional<Part>& part) {
	// Initialization sequence
	//
	// Reset CRC
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::RCRC)}));

	// NOP
	out_packets.emplace_back(new NopPacket());

	// Frame length
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::FLR,
	    {0x0380}));

	// Configuration Options 1
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::COR1,
	    {0x3d00}));

	// Configurations Options2
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::COR2,
	    {0x9ee}));

	// IDCODE
	out_packets.emplace_back(new ConfigurationPacketWithPayload<2>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::IDCODE,
	    {part->idcode() >> 16, part->idcode()}));

	// Control MASK
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::MASK,
	    {0xcf}));

	// Control options
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CTL,
	    {0x81}));

	// NOP packets
	for (int i = 0; i < 17; i++) {
		out_packets.emplace_back(new NopPacket());
	}

	// CCLK FREQ
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write,
	    ConfigurationRegister::CCLK_FREQ, {0x3cc8}));

	// PWRDN_REG
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write,
	    ConfigurationRegister::PWRDN_REG, {0x881}));

	// EYE MASK
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::EYE_MASK,
	    {0x0}));

	// House Clean Option
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write,
	    ConfigurationRegister::HC_OPT_REG, {0x1f}));

	// Configuration Watchdog Timer
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CWDT,
	    {0xffff}));

	// GWE cycle during wake-up from suspend
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::PU_GWE,
	    {0x5}));

	// GTS cycle during wake-up from suspend
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::PU_GTS,
	    {0x4}));

	// Reboot mode
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::MODE_REG,
	    {0x100}));

	// General options 1
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::GENERAL1,
	    {0x0}));

	// General options 2
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::GENERAL2,
	    {0x0}));

	// General options 3
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::GENERAL3,
	    {0x0}));

	// General options 4
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::GENERAL4,
	    {0x0}));

	// General options 5
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::GENERAL5,
	    {0x0}));

	// SEU frequency, enable and status
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::SEU_OPT,
	    {0x1be2}));

	// Expected readback signature for SEU detection
	out_packets.emplace_back(new ConfigurationPacketWithPayload<2>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::EXP_SIGN,
	    {0x0, 0x0}));

	// NOP
	out_packets.emplace_back(new NopPacket());
	out_packets.emplace_back(new NopPacket());

	// FAR
	out_packets.emplace_back(new ConfigurationPacketWithPayload<2>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::FAR_MAJ,
	    {0x0, 0x0}));

	// Write Configuration Data
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::WCFG)}));

	// Frame data write
	out_packets.emplace_back(new ConfigurationPacket(
	    2, ConfigurationPacket::Opcode::Write, ConfigurationRegister::FDRI,
	    {packet_data}));

	// NOP packets
	for (int i = 0; i < 24; i++) {
		out_packets.emplace_back(new NopPacket());
	}

	// Finalization sequence
	//
	// Set/reset the IOB and CLB flip-flops
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::GRESTORE)}));

	// Last Frame
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::LFRM)}));

	// NOP packets
	for (int i = 0; i < 4; i++) {
		out_packets.emplace_back(new NopPacket());
	}

	// Set/reset the IOB and CLB flip-flops
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::GRESTORE)}));

	// Startup sequence
	//
	// Start
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::START)}));

	// Control MASK
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::MASK,
	    {0xff}));

	// Control options
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CTL,
	    {0x81}));

	// CRC
	out_packets.emplace_back(new ConfigurationPacketWithPayload<2>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CRC,
	    {0x36, 0x6c47}));

	// Desync
	out_packets.emplace_back(new ConfigurationPacketWithPayload<1>(
	    ConfigurationPacket::Opcode::Write, ConfigurationRegister::CMD,
	    {static_cast<uint32_t>(Command::DESYNC)}));

	// NOP packets
	for (int i = 0; i < 14; i++) {
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

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray
