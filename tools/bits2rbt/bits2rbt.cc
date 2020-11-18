#include <gflags/gflags.h>
#include <fstream>
#include <iostream>

#include "configuration_packets.h"

DEFINE_string(o, "", "Output RBT file");
DEFINE_string(aux, "", "Input auxiliary data file");
DEFINE_string(arch, "Series7", "FPGA architecture");

int main(int argc, char** argv) {
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	if (argc != 2) {
		std::cerr << "Error: Input bits file not specified"
		          << std::endl;
		return 1;
	}

	std::ofstream out_file;
	if (!FLAGS_o.empty()) {
		out_file.open(FLAGS_o.c_str(), std::ofstream::out);
		if (!out_file.good()) {
			std::cerr << "Error: Can't open output file\n";
			return 1;
		}
	}
	std::ostream& out = (FLAGS_o.empty()) ? std::cout : out_file;

	try {
		std::shared_ptr<ConfigurationPackets> packets =
		    ConfigurationPackets::InitFromFile(argv[1], FLAGS_arch);
		packets->AddAuxData(FLAGS_aux);
		packets->WriteBits(out);
	} catch (std::runtime_error& e) {
		std::cerr << "Error: " << e.what();
		return 1;
	}

	if (!FLAGS_o.empty()) {
		out_file.close();
	}
	return 0;
}
