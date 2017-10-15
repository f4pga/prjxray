#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <assert.h>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>
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
			assert(segdata.count(token) == 0);
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

	int opt;
	while ((opt = getopt(argc, argv, "o:")) != -1)
		switch (opt)
		{
		case 'o':
			outfile = optarg;
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

	int min_candidates = num_bits;
	int max_candidates = 0;
	float avg_candidates = 0;

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
		min_candidates = std::min(min_candidates, num_candidates);
		max_candidates = std::max(max_candidates, num_candidates);
		avg_candidates += float(num_candidates) / num_tags;

		fprintf(f, "%s", tag_ids_r.at(tag_idx).c_str());

		if (0 < num_candidates && num_candidates <= 4) {
			for (int bit_idx = 0; bit_idx < num_bits; bit_idx++)
				if (mask.at(bit_idx))
					fprintf(f, " %s", bit_ids_r.at(bit_idx).c_str());
			fprintf(f, "\n");
		} else {
			fprintf(f, " <%d candidates>\n", num_candidates);
		}
	}

	printf("min #of candidates: %d\n", min_candidates);
	printf("max #of candidates: %d\n", max_candidates);
	printf("avg #of candidates: %f\n", avg_candidates);

	return 0;
}

