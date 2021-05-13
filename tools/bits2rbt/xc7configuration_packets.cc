#include <absl/strings/str_split.h>
#include <algorithm>
#include <bitset>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

#include "configuration_packets.h"
#include "crc.h"
#include "ecc.h"
#include "header.h"

ConfigurationPackets::ConfigurationPackets(const std::string& arch)
    : words_per_frame_(words_in_architecture.at(arch)),
      architecture_(arch),
      ecc_(arch, words_per_frame_) {}

const std::unordered_map<std::string, size_t>
    ConfigurationPackets::words_in_architecture = {{"Series7", 101},
                                                   {"UltraScale", 123},
                                                   {"UltraScalePlus", 93}};

std::shared_ptr<ConfigurationPackets> ConfigurationPackets::InitFromFile(
    const std::string& file,
    const std::string& arch) {
	std::ifstream ifs(file, std::ifstream::in);
	if (!ifs.good()) {
		throw std::runtime_error("Couldn't open bits file\n");
	}
	if (words_in_architecture.find(arch) == words_in_architecture.end()) {
		throw std::runtime_error("Error: Unrecognized architecture " +
		                         arch + "\n");
	}
	std::shared_ptr<ConfigurationPackets> packets =
	    std::make_shared<ConfigurationPackets>(arch);
	packets->SetBits(ifs);
	packets->UpdateECCs();
	return packets;
}

void ConfigurationPackets::SetBits(std::ifstream& ifs) {
	while (!ifs.eof()) {
		std::string line;
		getline(ifs, line);
		SetBit(line);
	}
}

void ConfigurationPackets::WriteBits(std::ostream& out) {
	header_->Write(out);
	WriteFpgaConfiguration(out, fpga_configuration_head_);
	WriteConfiguration(out);
	WriteFpgaConfiguration(out, fpga_configuration_tail_);
}

void ConfigurationPackets::WriteFpgaConfiguration(
    std::ostream& out,
    const std::vector<uint32_t>& vect) {
	for (auto& word : vect) {
		out << std::bitset<32>(word) << std::endl;
	}
}

void ConfigurationPackets::WriteConfiguration(std::ostream& out) {
	for (auto packet = configuration_data_packets_.cbegin();
	     packet != configuration_data_packets_.cend(); ++packet) {
		WritePacket(out, packet);
		if (IsDifferentRow(packet, std::next(packet))) {
			// Write the zero frame at the end of each row
			WritePacket(out, packet);
		}
	}
}

void ConfigurationPackets::WritePacket(
    std::ostream& out,
    ConfigurationFrames::const_iterator frame_citr) const {
	bool is_new_row(false);
	if ((frame_citr == configuration_data_packets_.cbegin()) ||
	    IsDifferentRow(frame_citr, std::prev(frame_citr))) {
		// Write the WCFG command followed by a FAR write with address
		// of the next frame WCFG command write
		out << std::bitset<32>(kCmdWrite | 0x1) << std::endl;
		out << std::bitset<32>(0x1) << std::endl;
		out << std::bitset<32>(kNop) << std::endl;
		// FAR Write of the next frame followed by frame address
		out << std::bitset<32>(kFarWrite | 0x1) << std::endl;
		out << std::bitset<32>(frame_citr->first) << std::endl;
		if (architecture_ == "Series7") {
			out << std::bitset<32>(kNop) << std::endl;
		}
		is_new_row = true;
	}
	uint32_t crc(GetCRC(frame_citr, is_new_row));
	// FDRI Write
	out << std::bitset<32>(kFdriWrite | words_per_frame_) << std::endl;
	// Declared number of configuration words
	for (auto& word : frame_citr->second) {
		out << std::bitset<32>(word) << std::endl;
	}
	// FAR Write followed by frame address
	out << std::bitset<32>(kFarWrite | 0x1) << std::endl;
	out << std::bitset<32>(frame_citr->first) << std::endl;
	// CRC Write followed by packet CRC
	out << std::bitset<32>(kCrcWrite | 0x1) << std::endl;
	out << std::bitset<32>(crc) << std::endl;
}

void ConfigurationPackets::SetBit(const std::string& line) {
	if (line.empty()) {
		return;
	}
	uint32_t frame_address, word, bit;
	sscanf(line.c_str(), "bit_%08x_%03u_%02u", &frame_address, &word, &bit);
	if (configuration_data_packets_.find(frame_address) ==
	    configuration_data_packets_.end()) {
		configuration_data_packets_[frame_address] =
		    std::vector<uint32_t>(words_per_frame_, 0x0);
	}
	configuration_data_packets_[frame_address].at(word) |= (1 << bit);
}

void ConfigurationPackets::Line2Vector(const std::string& line,
                                       std::vector<uint32_t>& vect) {
	static std::function<uint32_t(const std::string& str)> str_to_uint =
	    [](const std::string& str) -> uint32_t {
		assert(!str.empty());
		return std::stoul(str, nullptr, 16);
	};
	// Skip the line content description before the conversion
	std::vector<std::string> str_vector =
	    absl::StrSplit(line.substr(line.find(":") + 2), " ");
	std::transform(str_vector.begin(), str_vector.end(),
	               std::back_inserter(vect), str_to_uint);
}

void ConfigurationPackets::AddAuxData(const std::string& file) {
	std::ifstream ifs(file, std::ifstream::in);
	if (!ifs.good()) {
		throw std::runtime_error("Couldn't open auxiliary data file\n");
	}

	std::string line;
	getline(ifs, line);
	InitializeHeader(line);
	getline(ifs, line);
	InitializeFpgaConfigurationHead(line);
	getline(ifs, line);
	InitializeFpgaConfigurationTail(line);
	getline(ifs, line);
	InitializeConfigurationData(line);
}

uint32_t ConfigurationPackets::GetFpgaConfigurationCRC() const {
	uint32_t crc(0);
	auto far = std::search(fpga_configuration_head_.begin(),
	                       fpga_configuration_head_.end(), kRCrcCmd.begin(),
	                       kRCrcCmd.end());
	for (auto itr = far + kRCrcCmd.size();
	     itr != fpga_configuration_head_.end(); ++itr) {
		if (*itr == kNop)
			continue;
		// Check if it is a write packet
		assert(*itr & 0x30000000);
		// Get the packet address
		uint32_t addr = (*itr >> 13) & 0x1F;
		std::advance(itr, 1);
		assert(itr != fpga_configuration_head_.end());
		crc = icap_crc(addr, *itr, crc);
	}
	return crc;
}

uint32_t ConfigurationPackets::GetCRC(
    ConfigurationFrames::const_iterator frame_citr,
    bool is_new_row) const {
	uint32_t crc = 0;
	if (is_new_row) {
		if (frame_citr == configuration_data_packets_.begin()) {
			crc = GetFpgaConfigurationCRC();
		}
		crc = icap_crc(kCmdReg, kWcfgCmd, crc);
		crc = icap_crc(kFarReg, frame_citr->first, crc);
	}
	for (const auto& word : frame_citr->second) {
		crc = icap_crc(kFdriReg, word, crc);
	}
	crc = icap_crc(kFarReg, frame_citr->first, crc);
	return crc;
}

void ConfigurationPackets::UpdateECCs() {
	for (auto& packet : configuration_data_packets_) {
		auto& data = packet.second;
		ecc_.UpdateFrameECC(data);
	}
}

void ConfigurationPackets::InitializeConfigurationData(
    const std::string& line) {
	std::function<void(const uint32_t&)> update_packets =
	    [this](const uint32_t& addr) {
		    if (configuration_data_packets_.find(addr) ==
		        configuration_data_packets_.end()) {
			    configuration_data_packets_[addr] =
			        std::vector<uint32_t>(words_per_frame_, 0x0);
		    }
	    };
	std::vector<uint32_t> frames_addr;
	Line2Vector(line, frames_addr);
	std::for_each(frames_addr.begin(), frames_addr.end(), update_packets);
}

void ConfigurationPackets::InitializeFpgaConfigurationHead(
    const std::string& line) {
	Line2Vector(line, fpga_configuration_head_);
}

void ConfigurationPackets::InitializeFpgaConfigurationTail(
    const std::string& line) {
	Line2Vector(line, fpga_configuration_tail_);
}

void ConfigurationPackets::InitializeHeader(const std::string& line) {
	// FIXME Remove the configuration data head part once the aux data is
	// fixed
	header_ = std::make_unique<Header>(line, fpga_configuration_head_);
}

bool ConfigurationPackets::IsDifferentRow(
    ConfigurationFrames::const_iterator frame_citr1,
    ConfigurationFrames::const_iterator frame_citr2) const {
	auto get_row = [this](const uint32_t& address) {
		size_t row_shift =
		    (architecture_ == "UltraScalePlus") ? 18 : 17;
		return (address >> row_shift) & 0x3FF;
	};
	return (get_row(frame_citr1->first) != get_row(frame_citr2->first));
}
