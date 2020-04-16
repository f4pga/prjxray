/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <iostream>

#include <gflags/gflags.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_writer.h>
#include <prjxray/xilinx/configuration.h>

DEFINE_string(part_name, "", "Name of the 7-series part");
DEFINE_string(part_file, "", "Definition file for target 7-series part");
DEFINE_string(
    frm_file,
    "",
    "File containing a list of frame deltas to be applied to the base "
    "bitstream.  Each line in the file is of the form: "
    "<frame_address> <word1>,...,<word101>.");
DEFINE_string(output_file, "", "Write bitstream to file");
DEFINE_string(architecture,
              "Series7",
              "Architecture of the provided bitstream");

namespace xilinx = prjxray::xilinx;

struct Frames2BitWriter {
	template <typename T>
	int operator()(T& arg) {
		using ArchType = std::decay_t<decltype(arg)>;
		auto part = ArchType::Part::FromFile(FLAGS_part_file);
		if (!part) {
			std::cerr << "Part file " << FLAGS_part_file
			          << " not found or invalid" << std::endl;
			return 1;
		}

		// Read the frames from the input file
		xilinx::Frames<ArchType> frames;
		if (frames.readFrames(FLAGS_frm_file)) {
			std::cerr << "Frames file " << FLAGS_frm_file
			          << " not found or invalid" << std::endl;
			return 1;
		}

		if (std::is_same<ArchType, xilinx::Series7>::value ||
		    std::is_same<ArchType, xilinx::UltraScale>::value ||
		    std::is_same<ArchType, xilinx::UltraScalePlus>::value) {
			// In case the frames input file is missing some frames
			// that are in the tilegrid
			frames.addMissingFrames(part);
		}

		// Create data for the type 2 configuration packet with
		// information about all frames
		typename xilinx::Configuration<ArchType>::PacketData
		    configuration_packet_data(
		        xilinx::Configuration<ArchType>::
		            createType2ConfigurationPacketData(
		                frames.getFrames(), part));

		// Put together a configuration package
		typename ArchType::ConfigurationPackage configuration_package;
		xilinx::Configuration<ArchType>::createConfigurationPackage(
		    configuration_package, configuration_packet_data, part);

		// Write bitstream
		auto bitstream_writer =
		    xilinx::BitstreamWriter<ArchType>(configuration_package);
		if (bitstream_writer.writeBitstream(
		        configuration_package, FLAGS_part_name, FLAGS_frm_file,
		        "xc7frames2bit", FLAGS_output_file)) {
			std::cerr << "Failed to write bitstream" << std::endl
			          << "Exitting" << std::endl;
		}
		return 0;
	}
};

int main(int argc, char* argv[]) {
	gflags::SetUsageMessage(argv[0]);
	gflags::ParseCommandLineFlags(&argc, &argv, true);
	xilinx::Architecture::Container arch_container =
	    xilinx::ArchitectureFactory::create_architecture(
	        FLAGS_architecture);
	return absl::visit(Frames2BitWriter(), arch_container);
}
