#include <libgen.h>

#include <iomanip>
#include <iostream>
#include <sstream>

#include <absl/types/optional.h>
#include <absl/types/span.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/configuration_frame_address.h>
#include <yaml-cpp/yaml.h>

namespace xc7series = prjxray::xilinx::xc7series;

template<typename T>
std::string HexString(T value) {
	std::ostringstream out;
	out << "0x" << std::hex << value;
	return out.str();
}

int main(int argc, char *argv[]) {
	if (argc < 2) {
		std::cerr << "ERROR: no input specified" << std::endl;
		std::cerr << "Usage: " << basename(argv[0])
			  << " <bit_file>"
			  << std::endl;
		return 1;
	}

	auto in_file_name = argv[1];
	auto in_file = prjxray::MemoryMappedFile::InitWithFile(in_file_name);
	if (!in_file) {
		std::cerr << "Unable to open bit file: " << in_file_name
			  << std::endl;
		return 1;
	}

	auto in_bytes = absl::Span<uint8_t>(
			static_cast<uint8_t*>(in_file->data()),
			in_file->size());
	auto reader = xc7series::BitstreamReader::InitWithBytes(in_bytes);
	if (!reader) {
		std::cerr << "Input doesn't look like a bitstream"
			  << std::endl;
		return 1;
	}

	bool found_fdri_write = false;
	std::vector<uint32_t> frame_addresses;
	absl::optional<uint32_t> idcode;
	for (auto packet : *reader) {
		if (packet.opcode() !=
		     xc7series::ConfigurationPacket::Opcode::Write) {
			continue;
		}

		if (packet.address() ==
		    xc7series::ConfigurationRegister::FDRI) {
			found_fdri_write = true;
		} else if ((packet.address() ==
			    xc7series::ConfigurationRegister::IDCODE) &&
			   packet.data().size() == 1) {
			idcode = packet.data()[0];
		} else if (found_fdri_write &&
			   (packet.address() ==
			    xc7series::ConfigurationRegister::LOUT) &&
			   packet.data().size() == 1) {
			frame_addresses.push_back(packet.data()[0]);
		}
	}

	if (!idcode) {
		std::cerr << "No IDCODE found." << std::endl;
		return 1;
	}

	if (frame_addresses.empty()) {
		std::cerr << "No LOUT writes found.  Was "
			  << "BITSTREAM.GENERAL.DEBUGBITSTREAM set to YES?"
			  << std::endl;
		return 1;
	}

	YAML::Node config_yaml;
	config_yaml.SetTag("xilinx/xc7series/part");
	config_yaml["idcode"] = HexString(*idcode);

	// So far, the addresses appear to be written in increasing order but
	// there is no guarantee.  Sort them just in case.
	std::sort(frame_addresses.begin(), frame_addresses.end());

	YAML::Node regions = config_yaml["configuration_regions"];
	for (auto start_of_range = frame_addresses.begin();
	     start_of_range != frame_addresses.end();
	     ) {
		auto end_of_range = start_of_range;
		while (end_of_range + 1 != frame_addresses.end() &&
		       *(end_of_range + 1) == *end_of_range + 1) {
			++end_of_range;
		}

		YAML::Node region;
		region["start"] =
			xc7series::ConfigurationFrameAddress(*start_of_range);
		region["end"] =
			xc7series::ConfigurationFrameAddress(*end_of_range);
		regions.push_back(region);

		start_of_range = ++end_of_range;
	}

	std::cout << config_yaml << std::endl;

	return 0;
}
