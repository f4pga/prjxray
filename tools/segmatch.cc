/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <string>
#include <vector>

#include <absl/strings/str_cat.h>
#include <gflags/gflags.h>

DEFINE_int32(
    c,
    4,
    "threshold under which candidates are output. set to -1 to output all.");
DEFINE_bool(i, false, "add inverted tags");
DEFINE_int32(m, 0, "min number of set/cleared samples each");
DEFINE_int32(M, 0, "min number of set/cleared samples total");
DEFINE_string(o, "", "set output file");
DEFINE_string(k, "", "set output mask file");

using std::map;
using std::string;
using std::tuple;
using std::vector;

int num_bits = 0, num_tags = 0;
map<string, int> bit_ids, tag_ids;
vector<string> bit_ids_r, tag_ids_r;

#if 0
struct bool_vec
{
	vector<bool> data;

	bool_vec(int n = 0, bool initval = false) : data(n, initval)
	{
	}

	void set(int n)
	{
		if (int(data.size()) <= n)
			data.resize(n+1);
		data[n] = true;
	}

	bool get(int n)
	{
		return data.at(n);
	}

	void resize(int n)
	{
		data.resize(n);
	}

	int count()
	{
		return std::accumulate(data.begin(), data.end(), 0);
	}

	void apply_and(const bool_vec &other)
	{
		assert(data.size() == other.data.size());
		for (int i = 0; i < int(data.size()); i++)
			data[i] = data[i] && other.data[i];
	}

	void apply_andc(const bool_vec &other)
	{
		assert(data.size() == other.data.size());
		for (int i = 0; i < int(data.size()); i++)
			data[i] = data[i] && !other.data[i];
	}
};
#else
struct bool_vec {
	vector<uint64_t> data;

	bool_vec(int n = 0, bool initval = false)
	    : data((n + 63) / 64, initval ? ~uint64_t(0) : uint64_t(0)) {
		for (int i = data.size() * 64 - 1; i >= n; i--)
			data[n / 64] &= ~(uint64_t(1) << (n % 64));
	}

	void set(int n) {
		if (int(data.size() * 64) <= n)
			data.resize((n + 64) / 64);
		data[n / 64] |= uint64_t(1) << (n % 64);
	}

	bool get(int n) { return (data[n / 64] >> (n % 64)) & 1; }

	void resize(int n) { data.resize((n + 63) / 64); }

	int count() {
		int sum = 0;
		for (int i = 0; i < 64 * int(data.size()); i++)
			if (get(i))
				sum++;
		return sum;
	}

	void apply_and(const bool_vec& other) {
		assert(data.size() == other.data.size());
		for (int i = 0; i < int(data.size()); i++)
			data[i] &= other.data[i];
	}

	void apply_andc(const bool_vec& other) {
		assert(data.size() == other.data.size());
		for (int i = 0; i < int(data.size()); i++)
			data[i] &= ~other.data[i];
	}
};
#endif

// segname -> bits, tags_on, tags_off
typedef tuple<bool_vec, bool_vec, bool_vec> segdata_t;
map<string, segdata_t> segdata;

map<string, int> segnamecnt;

static inline bool_vec& segdata_bits(segdata_t& sd) {
	return std::get<0>(sd);
}
static inline bool_vec& segdata_tags1(segdata_t& sd) {
	return std::get<1>(sd);
}
static inline bool_vec& segdata_tags0(segdata_t& sd) {
	return std::get<2>(sd);
}

void read_input(std::istream& f, std::string filename) {
	string token;
	segdata_t* segptr = nullptr;

	while (f >> token) {
		if (token == "seg") {
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

		if (token == "bit") {
			assert(segptr != nullptr);

			f >> token;
			if (bit_ids.count(token) == 0) {
				bit_ids[token] = num_bits++;
				bit_ids_r.push_back(token);
			}

			int bit_idx = bit_ids.at(token);
			auto& bits = segdata_bits(*segptr);

			bits.set(bit_idx);
			continue;
		}

		if (token == "tag") {
			assert(segptr != nullptr);

			f >> token;
			if (tag_ids.count(token) == 0) {
				tag_ids[token] = num_tags++;
				tag_ids_r.push_back(token);
			}

			int tag_idx = tag_ids.at(token);

			f >> token;
			assert(token == "0" || token == "1");

			auto& tags = token == "1" ? segdata_tags1(*segptr)
			                          : segdata_tags0(*segptr);

			tags.set(tag_idx);

			if (FLAGS_i) {
				auto& inv_tags = token == "1"
				                     ? segdata_tags0(*segptr)
				                     : segdata_tags1(*segptr);

				token = tag_ids_r.at(tag_idx) + "__INV";

				if (tag_ids.count(token) == 0) {
					tag_ids[token] = num_tags++;
					tag_ids_r.push_back(token);
				}

				int inv_tag_idx = tag_ids.at(token);
				inv_tags.set(inv_tag_idx);
			}

			continue;
		}

		abort();
	}

	// printf("Number of segments: %d\n", int(segdata.size()));
	// printf("Number of bits: %d\n", num_bits);
	// printf("Number of tags: %d\n", num_tags);

	for (auto& segdat : segdata) {
		segdata_bits(segdat.second).resize(num_bits);
		segdata_tags1(segdat.second).resize(num_tags);
		segdata_tags0(segdat.second).resize(num_tags);
	}
}

int main(int argc, char** argv) {
	gflags::SetUsageMessage(
	    absl::StrCat("Usage: ", argv[0], " [options] file.."));
	gflags::ParseCommandLineFlags(&argc, &argv, true);

	if (argc > 1) {
		for (int optind = 1; optind < argc; optind++) {
			printf("Reading %s.\n", argv[optind]);
			std::ifstream f;
			f.open(argv[optind]);

			// Check if input file exists.
			if (!f.good()) {
				printf("ERROR: Input file does not exist!\n");
				return -1;
			}

			assert(!f.fail());
			read_input(f, argv[optind]);
		}
	} else {
		printf("Reading from stdin...\n");
		read_input(std::cin, "stdin");
	}

	printf("#of segments: %d\n", int(segdata.size()));
	printf("#of bits: %d\n", num_bits);
	printf("#of tags: %d\n", num_tags);

	FILE* f = stdout;

	if (!FLAGS_o.empty()) {
		f = fopen(FLAGS_o.c_str(), "w");
		assert(f != nullptr);
	}

	int cnt_const0 = 0;
	int cnt_const1 = 0;
	int cnt_candidates = 0;
	int min_candidates = num_bits;
	int max_candidates = 0;
	float avg_candidates = 0;

	std::vector<std::string> out_lines;

	for (int tag_idx = 0; tag_idx < num_tags; tag_idx++) {
		bool_vec mask(num_bits, true);
		int count1 = 0, count0 = 0;

		for (auto& segdat : segdata) {
			auto& sd = segdat.second;
			bool tag1 = segdata_tags1(sd).get(tag_idx);
			bool tag0 = segdata_tags0(sd).get(tag_idx);

			assert(!tag1 || !tag0);

			if (tag1) {
				count1++;
				mask.apply_and(segdata_bits(sd));
				continue;
			}

			if (tag0) {
				count0++;
				mask.apply_andc(segdata_bits(sd));
				continue;
			}
		}

		assert(count1 || count0);

		std::string out_line = tag_ids_r.at(tag_idx);

		if (count1 < FLAGS_m) {
			char buffer[64];
			snprintf(buffer, 64, " <m1 %d>", count1);
			out_line += buffer;
		}

		if (count0 < FLAGS_m) {
			char buffer[64];
			snprintf(buffer, 64, " <m0 %d>", count0);
			out_line += buffer;
		}

		if (count1 + count0 < FLAGS_M) {
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

		int num_candidates = mask.count();

		if (count0) {
			min_candidates =
			    std::min(min_candidates, num_candidates);
			max_candidates =
			    std::max(max_candidates, num_candidates);
			avg_candidates += num_candidates;
			cnt_candidates += 1;
		}

		if (FLAGS_c < 0 ||
		    (0 < num_candidates && num_candidates <= FLAGS_c)) {
			std::vector<std::string> out_tags;
			for (int bit_idx = 0; bit_idx < num_bits; bit_idx++)
				if (mask.get(bit_idx))
					out_tags.push_back(
					    bit_ids_r.at(bit_idx));
			std::sort(out_tags.begin(), out_tags.end());
			for (auto& tag : out_tags)
				out_line += " " + tag;
		} else {
			char buffer[64];
			snprintf(buffer, 64, " <%d candidates>",
			         num_candidates);
			out_line += buffer;
		}

		out_lines.push_back(out_line);
	}

	std::sort(out_lines.begin(), out_lines.end());

	for (auto& line : out_lines)
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

	if (!FLAGS_k.empty()) {
		f = fopen(FLAGS_k.c_str(), "w");
		assert(f != nullptr);
		std::sort(bit_ids_r.begin(), bit_ids_r.end());
		for (auto bit : bit_ids_r)
			fprintf(f, "bit %s\n", bit.c_str());
	}

	return 0;
}
