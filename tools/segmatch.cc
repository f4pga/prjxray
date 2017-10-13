#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <assert.h>
#include <vector>
#include <string>
#include <iostream>
#include <numeric>
#include <map>
#include <set>

using std::map;
using std::tuple;
using std::vector;
using std::string;

int num_bits = 0, num_tags = 0;
map<string, int> bit_ids, tag_ids;
vector<string> bit_ids_r, tag_ids_r;

// segname -> bits, tags_on, tags_off
typedef tuple<vector<bool>, vector<bool>, vector<bool>> segdata_t;
map<string, segdata_t> segdata;

static inline vector<bool> &segdata_bits(segdata_t &sd) { return std::get<0>(sd); }
static inline vector<bool> &segdata_tags1(segdata_t &sd) { return std::get<1>(sd); }
static inline vector<bool> &segdata_tags0(segdata_t &sd) { return std::get<2>(sd); }

void read_input()
{
	string token;
	segdata_t *segptr = nullptr;

	while (std::cin >> token)
	{
		if (token == "seg")
		{
			std::cin >> token;
			assert(segdata.count(token) == 0);
			segptr = &segdata[token];
			continue;
		}

		if (token == "bit")
		{
			assert(segptr != nullptr);

			std::cin >> token;
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

			std::cin >> token;
			if (tag_ids.count(token) == 0) {
				tag_ids[token] = num_tags++;
				tag_ids_r.push_back(token);
			}

			int tag_idx = tag_ids.at(token);

			std::cin >> token;
			assert(token == "0" || token == "1");

			auto &tags = token == "1" ? segdata_tags1(*segptr) : segdata_tags0(*segptr);

			if (int(tags.size()) <= tag_idx)
				tags.resize(tag_idx+1);

			tags[tag_idx] = true;
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
	int opt;
	while ((opt = getopt(argc, argv, "")) != -1)
		switch (opt)
		{
		// case 'c':
		// 	mode_c = true;
		// 	break;
		// case 'r':
		// 	mode_r = true;
		// 	break;
		// case 'm':
		// 	mode_m = true;
		// 	break;
		// case 'x':
		// 	mode_x = true;
		// 	break;
		// case 'y':
		// 	mode_y = true;
		// 	break;
		// case 'z':
		// 	mode_z = true;
		// 	break;
		// case 'C':
		// 	chksum = true;
		// 	break;
		// case 'f':
		// 	frames.insert(strtol(optarg, nullptr, 0));
		// 	break;
		// case 'o':
		// 	outfile = optarg;
		// 	break;
		default:
			goto help;
		}

	if (optind != argc) {
help:
		fprintf(stderr, "\n");
		fprintf(stderr, "Usage: %s [options] < segdata.txt\n", argv[0]);
		fprintf(stderr, "\n");
		// fprintf(stderr, "  -c\n");
		// fprintf(stderr, "    continuation mode. output '*' for repeating patterns\n");
		fprintf(stderr, "\n");
		return 1;
	}

	read_input();

	for (int tag_idx = 0; tag_idx < num_tags; tag_idx++)
	{
		vector<bool> mask(num_bits, true);

		for (auto &segdat : segdata)
		{
			auto &sd = segdat.second;

			if (segdata_tags1(sd).at(tag_idx)) {
				and_masks(mask, segdata_bits(sd));
				continue;
			}

			if (segdata_tags0(sd).at(tag_idx)) {
				andc_masks(mask, segdata_bits(sd));
				continue;
			}
		}

		int num_candidates = std::accumulate(mask.begin(), mask.end(), 0);

		printf("%s", tag_ids_r.at(tag_idx).c_str());

		if (0 < num_candidates && num_candidates <= 4) {
			for (int bit_idx = 0; bit_idx < num_bits; bit_idx++)
				if (mask.at(bit_idx))
					printf(" %s", bit_ids_r.at(bit_idx).c_str());
			printf("\n");
		} else {
			printf(" <%d candidates>\n", num_candidates);
		}
	}

	return 0;
}

