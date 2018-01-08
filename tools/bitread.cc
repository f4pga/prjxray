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
#include <absl/types/optional.h>
#include <gflags/gflags.h>
#include <prjxray/memory_mapped_file.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/configuration.h>
#include <prjxray/xilinx/xc7series/part.h>

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
DEFINE_string(part_file, "", "YAML file describing a Xilinx 7-Series part");

namespace xc7series = prjxray::xilinx::xc7series;

std::set<uint32_t> frames;
uint32_t frame_range_begin = 0, frame_range_end = 0;

std::vector<uint32_t> zero_frame(101);

int main(int argc, char** argv) {
	gflags::SetUsageMessage(
	    absl::StrCat("Usage: ", argv[0], " [options] [bitfile]"));
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	auto part = xc7series::Part::FromFile(FLAGS_part_file);
	if (!part) {
		std::cerr << "Part file not found or invalid" << std::endl;
		return 1;
	}

	if (FLAGS_f >= 0) {
		frames.insert(FLAGS_f);
	}

	if (!FLAGS_F.empty()) {
		std::pair<std::string, std::string> p =
		    absl::StrSplit(FLAGS_F, ":");
		frame_range_begin = strtol(p.first.c_str(), nullptr, 0);
		frame_range_end = strtol(p.second.c_str(), nullptr, 0) + 1;
	}

	absl::optional<xc7series::BitstreamReader> reader;
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

		reader = xc7series::BitstreamReader::InitWithBytes(
		    in_file->as_bytes());
	} else {
		std::vector<uint8_t> bitdata;
		while (1) {
			int c = getchar();
			if (c == EOF)
				break;
			bitdata.push_back(c);
		}

		std::cout << "Bitstream size: " << bitdata.size() << " bytes"
		          << std::endl;

		reader = xc7series::BitstreamReader::InitWithBytes(bitdata);
	}

	if (!reader) {
		std::cerr << "Bitstream does not appear to be a Xilinx "
		          << "7-series bitstream!" << std::endl;
		return 1;
	}

	std::cout << "Config size: " << reader->words().size() << " words"
	          << std::endl;

	auto config = xc7series::Configuration::InitWithPackets(*part, *reader);
	if (!config) {
		std::cerr << "Bitstream does not appear to be for this part"
		          << std::endl;
		return 1;
	}

	std::cout << "Number of configuration frames: "
	          << config->frames().size() << std::endl;

	FILE* f = stdout;

	if (!FLAGS_o.empty()) {
		f = fopen(FLAGS_o.c_str(), "w");

		if (f == nullptr) {
			printf("Can't open output file '%s' for writing!\n",
			       FLAGS_o.c_str());
			return 1;
		}
	} else {
		fprintf(f, "\n");
	}

	std::vector<std::vector<bool>> pgmdata;
	std::vector<int> pgmsep;

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
			    "Frame 0x%08x (Type=%d Top=%d Row=%d Column=%d "
			    "Minor=%d):\n",
			    static_cast<uint32_t>(it.first),
			    static_cast<unsigned int>(it.first.block_type()),
			    it.first.is_bottom_half_rows() ? 1 : 0,
			    it.first.row_address(), it.first.column_address(),
			    it.first.minor_address());

		if (FLAGS_p) {
			if (it.first.minor_address() == 0 && !pgmdata.empty())
				pgmsep.push_back(pgmdata.size());

			pgmdata.push_back(std::vector<bool>());

			for (int i = 0; i < 101; i++)
				for (int k = 0; k < 32; k++)
					pgmdata.back().push_back(
					    (it.second.at(i) & (1 << k)) != 0);
		} else if (FLAGS_x || FLAGS_y) {
			for (int i = 0; i < 101; i++)
				for (int k = 0; k < 32; k++)
					if ((i != 50 || k > 12 || FLAGS_C) &&
					    ((it.second.at(i) & (1 << k)) !=
					     0)) {
						if (FLAGS_x)
							fprintf(
							    f,
							    "bit_%08x_%03d_%"
							    "02d_t%d_h%d_r%d_c%"
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
							        .row_address(),
							    it.first
							        .column_address(),
							    it.first
							        .minor_address());
						else
							fprintf(f,
							        "bit_%08x_%03d_"
							        "%02d\n",
							        static_cast<
							            uint32_t>(
							            it.first),
							        i, k);
					}
			if (FLAGS_o.empty())
				fprintf(f, "\n");
		} else {
			if (!FLAGS_o.empty())
				fprintf(f, ".frame 0x%08x\n",
				        static_cast<uint32_t>(it.first));

			for (int i = 0; i < 101; i++)
				fprintf(f, "%08x%s",
				        it.second.at(i) &
				            ((i != 50 || FLAGS_C) ? 0xffffffff
				                                  : 0xffffe000),
				        (i % 6) == 5 ? "\n" : " ");
			fprintf(f, "\n\n");
		}
	}

	if (FLAGS_p) {
		int width = pgmdata.size() + pgmsep.size();
		int height = 101 * 32 + 100;
		fprintf(f, "P5 %d %d 15\n", width, height);

		for (int y = 0, bit = 101 * 32 - 1; y < height; y++, bit--) {
			for (int x = 0, frame = 0, sep = 0; x < width;
			     x++, frame++) {
				if (sep < int(pgmsep.size()) &&
				    frame == pgmsep.at(sep)) {
					fputc(8, f);
					x++, sep++;
				}

				fputc(pgmdata.at(frame).at(bit) ? 15 : 0, f);
			}

			if (bit % 32 == 0 && y) {
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
