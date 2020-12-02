/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include <iostream>
#include <set>
#include <string>
#include <vector>

#include <absl/strings/numbers.h>
#include <absl/strings/str_cat.h>
#include <absl/strings/str_split.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_reader.h>
#include <prjxray/xilinx/configuration.h>

DEFINE_bool(c, false, "output '*' for repeating patterns");
DEFINE_bool(C, false, "do not ignore the checksum in each frame");
DEFINE_int32(f,
             -1,
             "only dump the specified frame (might be used more than once)");
DEFINE_string(F,
              "",
              "<first_frame_address>:<last_frame_address> only dump frame in "
              "the specified range");
DEFINE_string(o, "", "write machine-readable output file with config frames");
DEFINE_bool(p, false, "output a binary netpgm image");
DEFINE_bool(x,
            false,
            "use format 'bit_%%08x_%%03d_%%02d_t%%d_h%%d_r%%d_c%%d_m%%d'\n"
            "The fields have the following meaning:\n"
            "  - complete 32 bit hex frame id\n"
            "  - word index with that frame (decimal)\n"
            "  - bit index with that word (decimal)\n"
            "  - decoded frame type from frame id\n"
            "  - decoded top/botttom from frame id (top=0)\n"
            "  - decoded row address from frame id\n"
            "  - decoded column address from frame id\n"
            "  - decoded minor address from frame id\n");
DEFINE_bool(y, false, "use format 'bit_%%08x_%%03d_%%02d'");
DEFINE_bool(z, false, "skip zero frames (frames with all bits cleared) in o");
DEFINE_string(part_file, "", "YAML file describing a Xilinx part");
DEFINE_string(architecture,
              "Series7",
              "Architecture of the provided bitstream");
DEFINE_string(
    aux,
    "",
    "write machine-readable output file with auxiliary bitstream data");

namespace xilinx = prjxray::xilinx;

std::set<uint32_t> frames;
uint32_t frame_range_begin = 0, frame_range_end = 0;

std::vector<uint32_t> zero_frame(101);

struct BitReader {
	BitReader(const std::vector<uint8_t>& bytes) : bytes_(bytes) {}

	const std::vector<uint8_t>& bytes_;

	template <typename T>
	int operator()(T& arg) {
		using ArchType = std::decay_t<decltype(arg)>;
		auto reader =
		    xilinx::BitstreamReader<ArchType>::InitWithBytes(bytes_);
		if (!reader) {
			std::cerr << "Input doesn't look like a bitstream"
			          << std::endl;
			return 1;
		}

		std::cout << "Config size: " << reader->words().size()
		          << " words" << std::endl;

		auto part = ArchType::Part::FromFile(FLAGS_part_file);
		if (!part) {
			std::cerr << "Part file not found or invalid"
			          << std::endl;
			return 1;
		}
		auto config = xilinx::Configuration<ArchType>::InitWithPackets(
		    *part, *reader);
		if (!config) {
			std::cerr
			    << "Bitstream does not appear to be for this part"
			    << std::endl;
			return 1;
		}

		std::cout << "Number of configuration frames: "
		          << config->frames().size() << std::endl;

		FILE* f = stdout;

		if (!FLAGS_o.empty()) {
			f = fopen(FLAGS_o.c_str(), "w");

			if (f == nullptr) {
				printf(
				    "Can't open output file '%s' for "
				    "writing!\n",
				    FLAGS_o.c_str());
				return 1;
			}
		} else {
			fprintf(f, "\n");
		}

		if (!FLAGS_aux.empty()) {
			FILE* aux_file = fopen(FLAGS_aux.c_str(), "w");
			if (aux_file == nullptr) {
				printf(
				    "Can't open aux output file '%s' for "
				    "writing!\n",
				    FLAGS_aux.c_str());
				return 1;
			}
			// Extract and decode header information as in RBT file
			xilinx::BitstreamReader<ArchType>::PrintHeader(
			    bytes_, aux_file);
			// Extract FPGA configuration logic information
			reader->PrintFpgaConfigurationLogicData(aux_file);
			// Extract configuration frames' addresses
			config->PrintFrameAddresses(aux_file);
			fclose(aux_file);
		}

		std::vector<std::vector<bool>> pgmdata;
		std::vector<int> pgmsep;

		int word_length = sizeof(typename ArchType::WordType) * 8;
		for (auto& it : config->frames()) {
			if (FLAGS_z && it.second == zero_frame)
				continue;

			if (!frames.empty() && !frames.count(it.first))
				continue;

			if (frame_range_begin != frame_range_end &&
			    (it.first < frame_range_begin ||
			     frame_range_end <= it.first))
				continue;

			if (FLAGS_o.empty())
				printf(
				    "Frame 0x%08x (Type=%d Top=%d Row=%d "
				    "Column=%d "
				    "Minor=%d):\n",
				    static_cast<uint32_t>(it.first),
				    static_cast<unsigned int>(
				        it.first.block_type()),
				    it.first.is_bottom_half_rows() ? 1 : 0,
				    it.first.row(), it.first.column(),
				    it.first.minor());

			if (FLAGS_p) {
				if (it.first.minor() == 0 && !pgmdata.empty())
					pgmsep.push_back(pgmdata.size());

				pgmdata.push_back(std::vector<bool>());

				for (size_t i = 0; i < it.second.size(); i++)
					for (int k = 0; k < word_length; k++)
						pgmdata.back().push_back(
						    (it.second.at(i) &
						     (1 << k)) != 0);
			} else if (FLAGS_x || FLAGS_y) {
				for (int i = 0; i < (int)it.second.size();
				     i++) {
					for (int k = 0; k < word_length; k++) {
						if (((i != 50 || k > 12 ||
						      FLAGS_C) ||
						     std::is_same<
						         ArchType,
						         prjxray::xilinx::
						             Spartan6>::
						         value) &&
						    ((it.second.at(i) &
						      (1 << k)) != 0)) {
							if (FLAGS_x)
								fprintf(
								    f,
								    "bit_%08x_%"
								    "03d_%"
								    "02d_t%d_h%"
								    "d_r%d_c%"
								    "d_m%d\n",
								    static_cast<
								        uint32_t>(
								        it.first),
								    i, k,
								    static_cast<
								        unsigned int>(
								        it.first
								            .block_type()),
								    it.first.is_bottom_half_rows()
								        ? 1
								        : 0,
								    it.first
								        .row(),
								    it.first
								        .column(),
								    it.first
								        .minor());
							else
								fprintf(
								    f,
								    "bit_%08x_%"
								    "03d_"
								    "%02d\n",
								    static_cast<
								        uint32_t>(
								        it.first),
								    i, k);
						}
					}
				}
				if (FLAGS_o.empty())
					fprintf(f, "\n");
			} else {
				if (!FLAGS_o.empty())
					fprintf(
					    f, ".frame 0x%08x\n",
					    static_cast<uint32_t>(it.first));

				for (size_t i = 0; i < it.second.size(); i++)
					if (std::is_same<ArchType,
					                 prjxray::xilinx::
					                     Spartan6>::value) {
						fprintf(
						    f, "%08x%s",
						    it.second.at(i) &
						        0xffffffff,
						    (i % 6) == 5 ? "\n" : " ");
					} else {
						fprintf(
						    f, "%08x%s",
						    it.second.at(i) &
						        ((i != 50 || FLAGS_C)
						             ? 0xffffffff
						             : 0xffffe000),
						    (i % 6) == 5 ? "\n" : " ");
					}

				fprintf(f, "\n\n");
			}
		}

		if (FLAGS_p) {
			int width = pgmdata.size() + pgmsep.size();
			int height = ArchType::words_per_frame * word_length;
			fprintf(f, "P5 %d %d 15\n", width, height);

			for (int y = 0,
			         bit = ArchType::words_per_frame * word_length -
			               1;
			     y < height; y++, bit--) {
				for (int x = 0, frame = 0, sep = 0; x < width;
				     x++, frame++) {
					if (sep < int(pgmsep.size()) &&
					    frame == pgmsep.at(sep)) {
						fputc(8, f);
						x++, sep++;
					}

					if (bit >=
					    (int)pgmdata.at(frame).size()) {
						fputc(0, f);
						continue;
					}

					fputc(
					    pgmdata.at(frame).at(bit) ? 15 : 0,
					    f);
				}

				if (bit % word_length == 0 && y) {
					for (int x = 0; x < width; x++)
						fputc(8, f);
					y++;
				}
			}
		}

		if (!FLAGS_o.empty())
			fclose(f);

		printf("DONE\n");
		return 0;
	}
};

int main(int argc, char** argv) {
	gflags::SetUsageMessage(
	    absl::StrCat("Usage: ", argv[0], " [options] [bitfile]"));
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	if (FLAGS_f >= 0) {
		frames.insert(FLAGS_f);
	}

	if (!FLAGS_F.empty()) {
		std::pair<std::string, std::string> p =
		    absl::StrSplit(FLAGS_F, ":");
		frame_range_begin = strtol(p.first.c_str(), nullptr, 0);
		frame_range_end = strtol(p.second.c_str(), nullptr, 0) + 1;
	}

	std::vector<uint8_t> in_bytes;
	if (argc == 2) {
		auto in_file_name = argv[1];
		auto in_file =
		    prjxray::MemoryMappedFile::InitWithFile(in_file_name);
		if (!in_file) {
			std::cerr << "Can't open input file '" << in_file_name
			          << "' for reading!" << std::endl;
			return 1;
		}

		std::cout << "Bitstream size: " << in_file->size() << " bytes"
		          << std::endl;

		in_bytes = std::vector<uint8_t>(
		    static_cast<uint8_t*>(in_file->data()),
		    static_cast<uint8_t*>(in_file->data()) + in_file->size());
	} else {
		while (1) {
			int c = getchar();
			if (c == EOF)
				break;
			in_bytes.push_back(c);
		}

		std::cout << "Bitstream size: " << in_bytes.size() << " bytes"
		          << std::endl;
	}

	xilinx::Architecture::Container arch_container =
	    xilinx::ArchitectureFactory::create_architecture(
	        FLAGS_architecture);
	return absl::visit(BitReader(in_bytes), arch_container);
}
