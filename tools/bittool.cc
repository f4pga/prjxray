#include <algorithm>
#include <iostream>

#include <absl/strings/str_cat.h>
#include <absl/types/span.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>

namespace xc7series = prjxray::xilinx::xc7series;

struct Action {
	std::string name;
	std::function<int(int, char*[])> handler;
};

int ListConfigPackets(int argc, char *argv[]) {
	if (argc < 1) {
		std::cerr << "ERROR: no input specified" << std::endl;
		std::cerr << "Usage: " << argv[0]
			  << "list_config_packets <bit_file>"
			  << std::endl;
		return 1;
	}

	auto in_file_name = argv[0];
	auto in_file = prjxray::MemoryMappedFile::InitWithFile(in_file_name);
	if (!in_file) {
		std::cerr << "Unable to open bit file: " << in_file_name
			  << std::endl;
		return 1;
	}

	auto reader = xc7series::BitstreamReader::InitWithBytes(
			in_file->as_bytes());
	if (!reader) {
		std::cerr << "Input doesn't look like a bitstream"
			  << std::endl;
		return 1;
	}

	for (auto packet : *reader) {
		std::cout << packet;
	}

	return 0;
}

int DumpDebugbitstreamFrameAddresses(int argc, char *argv[]) {
	if (argc < 1) {
		std::cerr << "ERROR: no input specified" << std::endl;
		std::cerr << "Usage: " << argv[0]
			  << "dump_debugbitstream_frame_addresses <bit_file>"
			  << std::endl;
		return 1;
	}

	auto in_file_name = argv[0];
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

	bool found_one_lout = false;
	for (auto packet : *reader) {
		if ((packet.opcode() !=
		     xc7series::ConfigurationPacket::Opcode::Write) ||
		    (packet.address() !=
		     xc7series::ConfigurationRegister::LOUT)) {
			continue;
		}

		if (packet.data().size() != 1) {
			std::cerr << "Write to FAR with word_count != 1"
				  << std::endl;
			continue;
		}

		found_one_lout = true;
		std::cout << std::dec << packet.data()[0] << std::endl;
	}

	if (!found_one_lout) {
		std::cerr << "No LOUT writes found.  Was "
			  << "BITSTREAM.GENERAL.DEBUGBITSTREAM set to YES?"
			  << std::endl;
		return 1;
	}

	return 0;
}

int GetDeviceId(int argc, char *argv[]) {
	if (argc < 1) {
		std::cerr << "ERROR: no input specified" << std::endl;
		std::cerr << "Usage: " << argv[0]
			  << "get_device_id <bit_file>"
			  << std::endl;
		return 1;
	}

	auto in_file_name = argv[0];
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

	auto idcode_packet = std::find_if(
		reader->begin(), reader->end(),
		[](const xc7series::ConfigurationPacket &packet) {
			return (packet.opcode() ==
				xc7series::ConfigurationPacket::Opcode::Write) &&
			       (packet.address() ==
				xc7series::ConfigurationRegister::IDCODE);
		});
	if (idcode_packet != reader->end()) {
		if (idcode_packet->data().size() != 1) {
			std::cerr << "Write to IDCODE with word_count != 1"
				  << std::endl;
			return 1;
		}

		std::cout << "0x" << std::hex << idcode_packet->data()[0]
			  << std::endl;
	}

	return 0;
}
int main(int argc, char *argv[]) {
	Action actions[] = {
		{ "list_config_packets", ListConfigPackets },
		{ "dump_debugbitstream_frame_addresses",
			DumpDebugbitstreamFrameAddresses },
		{ "get_device_id", GetDeviceId },
	};

	gflags::SetUsageMessage(
			absl::StrCat("Usage: ", argv[0], " [options] [bitfile]"));
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	if (argc < 2) {
		std::cerr << "ERROR: no command specified" << std::endl;
		std::cerr << "Usage: " << argv[0]
			  << "<command> <command_options>" << std::endl;
		return 1;
	}

	auto requested_action_str = argv[1];
	auto requested_action = std::find_if(
			std::begin(actions), std::end(actions),
			[&](const Action& t) {
				return t.name == requested_action_str; });
	if (requested_action == std::end(actions)) {
		std::cerr << "Unknown action: "
			  << requested_action_str << std::endl;
		return 1;
	}

	return requested_action->handler(argc - 2, argv + 2);
}
