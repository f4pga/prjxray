#include "header.h"
#include <algorithm>
#include <ctime>
#include <sstream>

Header::Header(const std::string& line,
               std::vector<uint32_t>& fpga_config_packets) {
	absl::string_view header_str(line);
	// Go to tag 'a' of the TLV formatted header
	header_str.remove_prefix(header_str.find("61"));
	bool tlv_header_end = false;
	while (!tlv_header_end) {
		char tag = char(GetByteAndAdvance(header_str));
		switch (tag) {
			case 'a':
				design_name_ = GetTLVHeaderValue(header_str);
				break;
			case 'b':
				part_ = GetTLVHeaderValue(header_str);
				break;
			case 'c':
				date_ = GetTLVHeaderValue(header_str);
				break;
			case 'd':
				date_ += " " + GetTLVHeaderValue(header_str);
				break;
			case 'e':
				// Get number of bytes in bitstream and multiply
				// by 8 to obtain number of bits
				no_bits_ = GetWord(header_str) * 8;
				tlv_header_end = true;
				break;
			default:
				assert(false);
		}
	}
	while (!header_str.empty()) {
		fpga_config_packets.emplace_back(GetWord(header_str));
	}
}

std::string Header::GetDate() {
	int year, month, day, hour, min, sec;
	std::replace_if(date_.begin(), date_.end(),
	                [](char c) { return c == '/' or c == ':'; }, ' ');
	std::istringstream(date_) >> year >> month >> day >> hour >> min >> sec;
	std::tm time_raw = {sec, min, hour, day, month - 1, year - 1900};
	time_t time = mktime(&time_raw);
	const std::tm* time_out = std::localtime(&time);
	return std::string(std::asctime(time_out));
}

std::string Header::GetArchitecture() {
	if (part_.find("xczu") != std::string::npos) {
		return "zynquplus";
	}
	if (part_.find("7a") != std::string::npos) {
		return "artix7";
	}
	if (part_.find("xcku") != std::string::npos) {
		return "kintexu";
	}
	return "Unknown architecture";
}

void Header::Write(std::ostream& out) {
	out << "Xilinx ASCII Bitstream" << std::endl;
	out << "Created by" << std::endl;
	out << "Design name:   " << design_name_ << std::endl;
	out << "Architecture:  " << GetArchitecture() << std::endl;
	out << "Part:          " << part_ << std::endl;
	out << "Date:          " << GetDate();
	out << "Bits:          " << no_bits_ << std::endl;
}

size_t Header::GetByteAndAdvance(absl::string_view& str_view) {
	size_t space_pos(str_view.find(" "));
	size_t byte =
	    std::stoul(std::string(str_view.substr(0, space_pos)), nullptr, 16);
	str_view.remove_prefix((space_pos != absl::string_view::npos)
	                           ? space_pos + 1
	                           : str_view.size());
	return byte;
}

size_t Header::GetTLVHeaderLength(absl::string_view& str_view) {
	return (GetByteAndAdvance(str_view) << 8) | GetByteAndAdvance(str_view);
}

std::string Header::GetTLVHeaderValue(absl::string_view& str_view) {
	size_t length(GetTLVHeaderLength(str_view));
	std::string value;
	for (size_t i = 0; i < length; i++) {
		value += char(GetByteAndAdvance(str_view));
	}
	// Lose trailing 0x00
	value.pop_back();
	return value;
}

uint32_t Header::GetWord(absl::string_view& str_view) {
	return (GetByteAndAdvance(str_view) << 24) |
	       (GetByteAndAdvance(str_view) << 16) |
	       (GetByteAndAdvance(str_view) << 8) | GetByteAndAdvance(str_view);
}
