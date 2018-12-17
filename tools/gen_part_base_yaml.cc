#include <libgen.h>

#include <algorithm>
#include <iostream>
#include <map>
#include <memory>
#include <vector>

#include <absl/types/optional.h>
#include <absl/types/span.h>
#include <absl/strings/str_cat.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <prjxray/xilinx/xc7series/global_clock_region.h>
#include <prjxray/xilinx/xc7series/part.h>
#include <yaml-cpp/yaml.h>

DEFINE_bool(i, false, "Print Device ID code only");

namespace xc7series = prjxray::xilinx::xc7series;

int main(int argc, char* argv[]) {
	gflags::SetUsageMessage(
		absl::StrCat("Usage: ", argv[0], " [bitfile] [options]"));

	gflags::ParseCommandLineFlags(&argc, &argv, true);

	if (argc < 2) {
		std::cerr << "ERROR: no input specified" << std::endl;
		std::cerr << "Usage: " << basename(argv[0]) << " <bit_file>"
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

	auto reader =
	    xc7series::BitstreamReader::InitWithBytes(in_file->as_bytes());
	if (!reader) {
		std::cerr << "Input doesn't look like a bitstream" << std::endl;
		return 1;
	}

	bool found_fdri_write = false;
	std::vector<xc7series::FrameAddress> frame_addresses;
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

	if (FLAGS_i) {
		std::cout << *idcode << std::endl;
		return 0;
	}

	if (frame_addresses.empty()) {
		std::cerr << "No LOUT writes found.  Was "
		          << "BITSTREAM.GENERAL.DEBUGBITSTREAM set to YES?"
		          << std::endl;
		return 1;
	}

	auto part = xc7series::Part(*idcode, frame_addresses.begin(),
	                            frame_addresses.end());
	std::cout << YAML::Node(part) << std::endl;

	return 0;
}
