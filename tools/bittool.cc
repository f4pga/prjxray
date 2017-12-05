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

int main(int argc, char *argv[]) {
	Action actions[] = {
		{ "list_config_packets", ListConfigPackets },
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
