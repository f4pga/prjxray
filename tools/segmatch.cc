#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <assert.h>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <numeric>
#include <algorithm>
#include <map>
#include <set>

using std::map;
using std::tuple;
using std::vector;
using std::string;

bool mode_inv = false;

int num_bits = 0, num_tags = 0;
map<string, int> bit_ids, tag_ids;
vector<string> bit_ids_r, tag_ids_r;

// segname -> bits, tags_on, tags_off
typedef tuple<vector<bool>, vector<bool>, vector<bool>> segdata_t;
map<string, segdata_t> segdata;

map<string, int> segnamecnt;

static inline vector<bool> &segdata_bits(segdata_t &sd) { return std::get<0>(sd); }
static inline vector<bool> &segdata_tags1(segdata_t &sd) { return std::get<1>(sd); }
static inline vector<bool> &segdata_tags0(segdata_t &sd) { return std::get<2>(sd); }

void read_input(std::istream &f, std::string filename)
{
	string token;
	segdata_t *segptr = nullptr;

	while (f >> token)
	{
		if (token == "seg")
		{
			f >> token;
			token = filename + ":" + token;
			while (segdata.count(token)) {
				int idx = 1;
				if (segnamecnt.count(token))
					idx = segnamecnt.at(token);
				segnamecnt[token] = idx + 1;
				char buffer[64];
				snprintf(buffer, 64, "-%d", idx);
				token += buffer;
			}
			segptr = &segdata[token];
			continue;
		}

		if (token == "bit")
		{
			assert(segptr != nullptr);

			f >> token;
			if (bit_ids.count(token) == 0) {
				bit_ids[token] = num_bits++;
				bit_ids_r.push_back(token);
			}

			int bit_idx = bit_ids.at(token);
			auto &bits = segdata_bits(*segptr);

			if (int(bits.size()) <= bit_idx)
				bits.resize(bit_idx+1);

			bits[bit_idx] = true;
			continue;
		}

		if (token == "tag")
		{
			assert(segptr != nullptr);

			f >> token;
			if (tag_ids.count(token) == 0) {
				tag_ids[token] = num_tags++;
				tag_ids_r.push_back(token);
			}

			int tag_idx = tag_ids.at(token);

			f >> token;
			assert(token == "0" || token == "1");

			auto &tags = token == "1" ? segdata_tags1(*segptr) : segdata_tags0(*segptr);

			if (int(tags.size()) <= tag_idx)
				tags.resize(tag_idx+1);

			tags[tag_idx] = true;

			if (mode_inv)
			{
				auto &inv_tags = token == "1" ? segdata_tags0(*segptr) : segdata_tags1(*segptr);

				token = tag_ids_r.at(tag_idx) + "__INV";

				if (tag_ids.count(token) == 0) {
					tag_ids[token] = num_tags++;
					tag_ids_r.push_back(token);
				}

				int inv_tag_idx = tag_ids.at(token);

				if (int(inv_tags.size()) <= inv_tag_idx)
					inv_tags.resize(inv_tag_idx+1);

				inv_tags[inv_tag_idx] = true;
			}

			continue;
		}

		abort();
	}

	// printf("Number of segments: %d\n", int(segdata.size()));
	// printf("Number of bits: %d\n", num_bits);
	// printf("Number of tags: %d\n", num_tags);

	for (auto &segdat : segdata) {
		segdata_bits(segdat.second).resize(num_bits);
		segdata_tags1(segdat.second).resize(num_tags);
		segdata_tags0(segdat.second).resize(num_tags);
	}
}

void and_masks(vector<bool> &dst_mask, const vector<bool> &src_mask)
{
	assert(dst_mask.size() == src_mask.size());
	for (int i = 0; i < int(dst_mask.size()); i++)
		dst_mask[i] = dst_mask[i] && src_mask[i];
}

void andc_masks(vector<bool> &dst_mask, const vector<bool> &src_mask)
{
	assert(dst_mask.size() == src_mask.size());
	for (int i = 0; i < int(dst_mask.size()); i++)
		dst_mask[i] = dst_mask[i] && !src_mask[i];
}

int main(int argc, char **argv)
{
	const char *outfile = nullptr;
	int min_each = 0, min_total = 0;
	int candidate_output_limit = 4;

	int opt;
	while ((opt = getopt(argc, argv, "c:io:m:M:")) != -1)
		switch (opt)
		{
		case 'o':
			outfile = optarg;
			break;
		case 'm':
			min_each = atoi(optarg);
			break;
		case 'M':
			min_total = atoi(optarg);
			break;
		case 'i':
			mode_inv = true;
			break;
		case 'c':
			candidate_output_limit = atoi(optarg);
			break;
		default:
			goto help;
		}

	if (0) {
help:
		fprintf(stderr, "\n");
		fprintf(stderr, "Usage: %s [options] file..\n", argv[0]);
		fprintf(stderr, "\n");
		fprintf(stderr, "  -o <filename>\n");
		fprintf(stderr, "    set output file\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -m <int>\n");
		fprintf(stderr, "    min number of set/cleared samples each\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -M <int>\n");
		fprintf(stderr, "    min number of set/cleared samples total\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -i\n");
		fprintf(stderr, "    add inverted tags\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -c <int>\n");
		fprintf(stderr, "    threshold under which candidates are output\n");
		fprintf(stderr, "    set to -1 to output all\n");
		fprintf(stderr, "\n");
		return 1;
	}

	if (optind != argc) {
		while (optind != argc) {
			printf("Reading %s.\n", argv[optind]);
			std::ifstream f;
			f.open(argv[optind]);
			assert(!f.fail());
			read_input(f, argv[optind++]);
		}
	} else {
		printf("Reading from stding.\n");
		read_input(std::cin, "stdin");
	}

	printf("#of segments: %d\n", int(segdata.size()));
	printf("#of bits: %d\n", num_bits);
	printf("#of tags: %d\n", num_tags);

	FILE *f = stdout;

	if (outfile) {
		f = fopen(outfile, "w");
		assert(f != nullptr);
	}

	int cnt_const0 = 0;
	int cnt_const1 = 0;
	int cnt_candidates = 0;
	int min_candidates = num_bits;
	int max_candidates = 0;
	float avg_candidates = 0;

	std::vector<std::string> out_lines;

	for (int tag_idx = 0; tag_idx < num_tags; tag_idx++)
	{
		vector<bool> mask(num_bits, true);
		int count1 = 0, count0 = 0;

		for (auto &segdat : segdata)
		{
			auto &sd = segdat.second;
			bool tag1 = segdata_tags1(sd).at(tag_idx);
			bool tag0 = segdata_tags0(sd).at(tag_idx);

			assert(!tag1 || !tag0);

			if (tag1) {
				count1++;
				and_masks(mask, segdata_bits(sd));
				continue;
			}

			if (tag0) {
				count0++;
				andc_masks(mask, segdata_bits(sd));
				continue;
			}
		}

		assert(count1 || count0);

		std::string out_line = tag_ids_r.at(tag_idx);

		if (count1 < min_each) {
			char buffer[64];
			snprintf(buffer, 64, " <m1 %d>", count1);
			out_line += buffer;
		}

		if (count0 < min_each) {
			char buffer[64];
			snprintf(buffer, 64, " <m0 %d>", count0);
			out_line += buffer;
		}

		if (count1 + count0 < min_total) {
			char buffer[64];
			snprintf(buffer, 64, " <M %d %d>", count1, count0);
			out_line += buffer;
		}

		if (!count1) {
			out_lines.push_back(out_line + " <const0>");
			cnt_const0 += 1;
			continue;
		}

		if (!count0) {
			out_line += " <const1>";
			cnt_const1 += 1;
		}

		int num_candidates = std::accumulate(mask.begin(), mask.end(), 0);

		if (count0) {
			min_candidates = std::min(min_candidates, num_candidates);
			max_candidates = std::max(max_candidates, num_candidates);
			avg_candidates += num_candidates;
			cnt_candidates += 1;
		}

		if (candidate_output_limit < 0 ||
		    (0 < num_candidates &&
		     num_candidates <= candidate_output_limit)) {
			std::vector<std::string> out_tags;
			for (int bit_idx = 0; bit_idx < num_bits; bit_idx++)
				if (mask.at(bit_idx))
					out_tags.push_back(bit_ids_r.at(bit_idx));
			std::sort(out_tags.begin(), out_tags.end());
			for (auto &tag : out_tags)
				out_line += " " + tag;
		} else {
			char buffer[64];
			snprintf(buffer, 64, " <%d candidates>", num_candidates);
			out_line += buffer;
		}

		out_lines.push_back(out_line);
	}

	std::sort(out_lines.begin(), out_lines.end());

	for (auto &line : out_lines)
		fprintf(f, "%s\n", line.c_str());

	if (cnt_candidates)
		avg_candidates /= cnt_candidates;

	printf("#of const0 tags: %d\n", cnt_const0);
	printf("#of const1 tags: %d\n", cnt_const1);

	if (cnt_candidates) {
		printf("min #of candidates: %d\n", min_candidates);
		printf("max #of candidates: %d\n", max_candidates);
		printf("avg #of candidates: %.3f\n", avg_candidates);
	}

	return 0;
}

