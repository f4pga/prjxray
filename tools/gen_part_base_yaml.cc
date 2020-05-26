/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <libgen.h>

#include <algorithm>
#include <iostream>
#include <map>
#include <memory>
#include <vector>

#include <absl/strings/str_cat.h>
#include <absl/types/optional.h>
#include <absl/types/span.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_reader.h>
#include <yaml-cpp/yaml.h>

DEFINE_bool(f, false, "Use FAR registers instead of LOUT ones");

namespace xilinx = prjxray::xilinx;

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

	auto reader = xilinx::BitstreamReader<xilinx::Series7>::InitWithBytes(
	    in_file->as_bytes());
	if (!reader) {
		std::cerr << "Input doesn't look like a bitstream" << std::endl;
		return 1;
	}

	bool found_fdri_write = false;
	std::vector<xilinx::Series7::FrameAddress> frame_addresses;
	absl::optional<uint32_t> idcode;
	for (auto packet : *reader) {
		if (packet.opcode() !=
		    xilinx::ConfigurationPacket<
		        xilinx::Series7::ConfRegType>::Opcode::Write) {
			continue;
		}

		if (packet.address() == xilinx::Series7::ConfRegType::FDRI) {
			found_fdri_write = true;
		} else if ((packet.address() ==
		            xilinx::Series7::ConfRegType::IDCODE) &&
		           packet.data().size() == 1) {
			idcode = packet.data()[0];
		} else if (found_fdri_write &&
		           (packet.address() ==
		            xilinx::Series7::ConfRegType::LOUT) &&
		           (packet.data().size() == 1) && FLAGS_f == false) {
			frame_addresses.push_back(packet.data()[0]);
			found_fdri_write = false;
		} else if (found_fdri_write &&
		           (packet.address() ==
		            xilinx::Series7::ConfRegType::FAR) &&
		           (packet.data().size() == 1) && FLAGS_f == true) {
			frame_addresses.push_back(packet.data()[0]);
			found_fdri_write = false;
		}
	}

	if (!idcode) {
		std::cerr << "No IDCODE found." << std::endl;
		return 1;
	}

	if (frame_addresses.empty()) {
		std::cerr << "No LOUT or FAR writes found.  Was "
		          << "BITSTREAM.GENERAL.DEBUGBITSTREAM or "
		          << "BITSTREAM.GENERAL.PERFRAMECRC set to YES?"
		          << std::endl;
		return 1;
	}

	auto part = xilinx::Series7::Part(*idcode, frame_addresses.begin(),
	                                  frame_addresses.end());
	std::cout << YAML::Node(part) << std::endl;

	return 0;
}
