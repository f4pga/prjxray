#include <iostream>

#include <absl/strings/str_cat.h>
#include <absl/types/span.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>

namespace xc7series = prjxray::xilinx::xc7series;

DEFINE_string(action, "list_config_packets", "");

struct Action {
	std::string name;
	std::function<int(int, char*[])> handler;
};

int ListConfigPackets(int argc, char *argv[]) {
	auto in_file = prjxray::MemoryMappedFile::InitWithFile(argv[1]);
	if (!in_file) {
		std::cerr << "Unable to open bit file: " << argv[1]
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

int main(int argc, char *argv[]) {
	Action actions[] = {
		{ "list_config_packets", ListConfigPackets },
		{ "dump_debugbitstream_frame_addresses",
			DumpDebugbitstreamFrameAddresses },
	};

	gflags::SetUsageMessage(
			absl::StrCat("Usage: ", argv[0], " [options] [bitfile]"));
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	if (argc != 2) {
		std::cerr << "no input file provided" << std::endl;
		return 1;
	}

	if (FLAGS_action.empty()) {
		std::cerr << "no action specified" << std::endl;
		return 1;
	}

	auto requested_action = std::find_if(
			std::begin(actions), std::end(actions),
			[](const Action& t) { return t.name == FLAGS_action; });
	if (requested_action == std::end(actions)) {
		std::cerr << "Unknown action: " << FLAGS_action << std::endl;
		return 1;
	}

	return requested_action->handler(argc, argv);
}
