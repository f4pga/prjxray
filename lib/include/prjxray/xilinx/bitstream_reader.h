/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_BITSTREAM_READER_H
#define PRJXRAY_LIB_XILINX_BITSTREAM_READER_H

#include <algorithm>
#include <iostream>
#include <memory>
#include <vector>

#include <absl/types/span.h>

#include <prjxray/big_endian_span.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/configuration_packet.h>

namespace prjxray {
namespace xilinx {

// Constructs a collection of 32-bit big-endian words from a bitstream file.
// Provides an iterator over the configuration packets.
template <typename ArchType>
class BitstreamReader {
       public:
	using value_type = ConfigurationPacket<typename ArchType::ConfRegType>;

	// Implements an iterator over the words grouped in configuration
	// packets.
	class iterator {
	       public:	        
	        using iterator_category = std::input_iterator_tag;
        	using value_type = BitstreamReader::value_type;
        	using difference_type = std::ptrdiff_t;
        	using pointer = value_type*;
        	using reference = value_type&;
        	
		iterator& operator++();

		bool operator==(const iterator& other) const;
		bool operator!=(const iterator& other) const;

		const value_type& operator*() const;
		const value_type* operator->() const;

	       protected:
		explicit iterator(absl::Span<uint32_t> words);

	       private:
		friend BitstreamReader;

		typename value_type::ParseResult parse_result_;
		absl::Span<uint32_t> words_;
	};

	// Construct a reader from a collection of 32-bit, big-endian words.
	// Assumes that any sync word has already been removed.
	BitstreamReader(std::vector<uint32_t>&& words)
	    : words_(std::move(words)) {}

	BitstreamReader() {}
	size_t size() { return words_.size(); }

	// Construct a `BitstreamReader` from a Container of bytes.
	// Any bytes preceding an initial sync word are ignored.
	template <typename T>
	static absl::optional<BitstreamReader<ArchType>> InitWithBytes(
	    T bitstream);

	// Extract information from bitstream necessary to reconstruct RBT
	// header and add it to the AUX data
	template <typename T>
	static void PrintHeader(T bitstream, FILE* aux_fp);

	// Extract configuration logic data and add to the AUX data
	void PrintFpgaConfigurationLogicData(FILE* aux_fp);

	const std::vector<uint32_t>& words() { return words_; };

	// Returns an iterator that yields `ConfigurationPackets`
	// as read from the bitstream.
	iterator begin();
	iterator end();

       private:
	static const std::array<uint8_t, 4> kSyncWord;
	static const std::array<uint32_t, 2> kWcfgCmd;
	static const std::array<uint32_t, 2> kNullCmd;

	std::vector<uint32_t> words_;
};

// Extract FPGA configuration logic information
template <typename ArchType>
void BitstreamReader<ArchType>::PrintFpgaConfigurationLogicData(FILE* aux_fp) {
	// Get the data before the first FDRI_WRITE command packet
	const auto fpga_conf_end = std::search(
	    words_.cbegin(), words_.cend(), kWcfgCmd.cbegin(), kWcfgCmd.cend());
	fprintf(aux_fp, "FPGA configuration logic prefix:");
	for (auto it = words_.cbegin(); it != fpga_conf_end; ++it) {
		fprintf(aux_fp, " %08X", *it);
	}
	fprintf(aux_fp, "\n");

	// Get the data after the last Null Command packet
	const auto last_null_cmd = std::find_end(
	    words_.cbegin(), words_.cend(), kNullCmd.cbegin(), kNullCmd.cend());
	fprintf(aux_fp, "FPGA configuration logic suffix:");
	for (auto it = last_null_cmd; it != words_.cend(); ++it) {
		fprintf(aux_fp, " %08X", *it);
	}
	fprintf(aux_fp, "\n");
}

template <typename ArchType>
template <typename T>
void BitstreamReader<ArchType>::PrintHeader(T bitstream, FILE* aux_fp) {
	// If this is really a Xilinx bitstream, there will be a sync
	// word somewhere toward the beginning.
	auto sync_pos = std::search(bitstream.begin(), bitstream.end(),
	                            kSyncWord.begin(), kSyncWord.end());
	if (sync_pos == bitstream.end()) {
		return;
	}
	sync_pos += kSyncWord.size();
	// Wrap the provided container in a span that strips off the preamble.
	absl::Span<typename T::value_type> bitstream_span(bitstream);
	auto header_packets =
	    bitstream_span.subspan(0, sync_pos - bitstream.begin());

	fprintf(aux_fp, "Header bytes:");
	for (auto& word : header_packets) {
		fprintf(aux_fp, " %02X", word);
	}
	fprintf(aux_fp, "\n");
}

template <typename ArchType>
template <typename T>
absl::optional<BitstreamReader<ArchType>>
BitstreamReader<ArchType>::InitWithBytes(T bitstream) {
	// If this is really a Xilinx bitstream, there will be a sync
	// word somewhere toward the beginning.
	auto sync_pos = std::search(bitstream.begin(), bitstream.end(),
	                            kSyncWord.begin(), kSyncWord.end());
	if (sync_pos == bitstream.end()) {
		return absl::optional<BitstreamReader<ArchType>>();
	}
	sync_pos += kSyncWord.size();

	// Wrap the provided container in a span that strips off the preamble.
	absl::Span<typename T::value_type> bitstream_span(bitstream);
	auto config_packets =
	    bitstream_span.subspan(sync_pos - bitstream.begin());

	// Convert the bytes into 32-bit or 16-bit in case of Spartan6,
	// big-endian words.
	auto big_endian_reader =
	    make_big_endian_span<typename ArchType::WordType>(config_packets);
	std::vector<uint32_t> words{big_endian_reader.begin(),
	                            big_endian_reader.end()};

	return BitstreamReader<ArchType>(std::move(words));
}

// Sync word as specified in UG470 page 81
template <typename ArchType>
const std::array<uint8_t, 4> BitstreamReader<ArchType>::kSyncWord{0xAA, 0x99,
                                                                  0x55, 0x66};

// Writing the WCFG(0x1) command in type 1 packet with 1 word to the CMD
// register (0x30008001) Refer to UG470 page 110
template <typename ArchType>
const std::array<uint32_t, 2> BitstreamReader<ArchType>::kWcfgCmd = {0x30008001,
                                                                     0x1};

// Writing the NULL(0x0) command in type 1 packet with 1 word to the CMD
// register (0x30008001) Refer to UG470 page 110
template <typename ArchType>
const std::array<uint32_t, 2> BitstreamReader<ArchType>::kNullCmd = {0x30008001,
                                                                     0x0};

template <typename ArchType>
typename BitstreamReader<ArchType>::iterator
BitstreamReader<ArchType>::begin() {
	return iterator(absl::MakeSpan(words_));
}

template <typename ArchType>
typename BitstreamReader<ArchType>::iterator BitstreamReader<ArchType>::end() {
	return iterator({});
}

template <typename ArchType>
BitstreamReader<ArchType>::iterator::iterator(absl::Span<uint32_t> words) {
	parse_result_.first = words;
	parse_result_.second = {};
	++(*this);
}

template <typename ArchType>
typename BitstreamReader<ArchType>::iterator&
    BitstreamReader<ArchType>::iterator::operator++() {
	do {
		auto new_result =
		    ConfigurationPacket<typename ArchType::ConfRegType>::
		        InitWithWords(parse_result_.first,
		                      parse_result_.second.has_value()
		                          ? parse_result_.second.operator->()
		                          : nullptr);

		// If the a valid header is being found but there are
		// insufficient words to yield a packet, consider it the end.
		if (new_result.first == parse_result_.first) {
			words_ = absl::Span<uint32_t>();
			break;
		}

		words_ = parse_result_.first;
		parse_result_ = new_result;
	} while (!parse_result_.first.empty() && !parse_result_.second);

	if (!parse_result_.second) {
		words_ = absl::Span<uint32_t>();
	}

	return *this;
}

template <typename ArchType>
bool BitstreamReader<ArchType>::iterator::operator==(
    const iterator& other) const {
	return words_ == other.words_;
}

template <typename ArchType>
bool BitstreamReader<ArchType>::iterator::operator!=(
    const iterator& other) const {
	return !(*this == other);
}

template <typename ArchType>
const typename BitstreamReader<ArchType>::value_type&
    BitstreamReader<ArchType>::iterator::operator*() const {
	return *(parse_result_.second);
}

template <typename ArchType>
const typename BitstreamReader<ArchType>::value_type*
    BitstreamReader<ArchType>::iterator::operator->() const {
	return parse_result_.second.operator->();
}
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_BITSTREAM_READER_H
