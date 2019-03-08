#include <iostream>

#include <gflags/gflags.h>
#include <prjxray/xilinx/xc7series/utils.h>

DEFINE_string(part_name, "", "Name of the 7-series part");
DEFINE_string(part_file, "", "Definition file for target 7-series part");
DEFINE_string(
    frm_file,
    "",
    "File containing a list of frame deltas to be applied to the base "
    "bitstream.  Each line in the file is of the form: "
    "<frame_address> <word1>,...,<word101>.");
DEFINE_string(output_file, "", "Write bitsteam to file");

namespace xc7series = prjxray::xilinx::xc7series;

int main(int argc, char* argv[]) {
	gflags::SetUsageMessage(argv[0]);
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	auto part = xc7series::Part::FromFile(FLAGS_part_file);
	if (!part) {
		std::cerr << "Part file " << FLAGS_part_file
		          << " not found or invalid" << std::endl;
		return 1;
	}

	// Read the frames from the input file
	xc7series::Frames frames;
	if (frames.readFrames(FLAGS_frm_file)) {
		std::cerr << "Frames file " << FLAGS_frm_file
		          << " not found or invalid" << std::endl;
		return 1;
	}

	// In case the frames input file is missing some frames that are in the
	// tilegrid
	frames.addMissingFrames(part);

	// Create data for the type 2 configuration packet with information
	// about all frames
	xc7series::PacketData configuration_packet_data(
	    xc7series::createType2ConfigurationPacketData(frames.getFrames(),
	                                                  part));

	// Put together a configuration package
	xc7series::ConfigurationPackage configuration_package;
	xc7series::createConfigurationPackage(configuration_package,
	                                      configuration_packet_data, part);

	// Write bitstream
	if (xc7series::writeBitstream(configuration_package, FLAGS_part_name,
	                              FLAGS_frm_file, "xc7frames2bit",
	                              FLAGS_output_file)) {
		std::cerr << "Failed to write bitstream" << std::endl
		          << "Exitting" << std::endl;
	}

	return 0;
}
