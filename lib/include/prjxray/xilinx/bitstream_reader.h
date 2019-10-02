#ifndef PRJXRAY_LIB_XILINX_BITSTREAM_READER_H
#define PRJXRAY_LIB_XILINX_BITSTREAM_READER_H

#include <algorithm>
#include <iostream>
#include <memory>
#include <vector>
#include <optional>

#include <absl/types/span.h>

#include <prjxray/big_endian_span.h>
#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/architectures.h>

namespace prjxray {
namespace xilinx {

template <typename ArchType>
class BitstreamReader {
       public:
	using value_type = ConfigurationPacket<typename ArchType::ConfRegType>;

	class iterator
	    : public std::iterator<std::input_iterator_tag, value_type> {
	       public:
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

	// Construct a reader from a collection of 16-bit, big-endian words.
	// Assumes that any sync word has already been removed.
	BitstreamReader(std::vector<uint32_t>&& words)
    		: words_(std::move(words)) {}

	BitstreamReader() {}
	size_t size() {
		return words_.size();
	}

	// Construct a `BitstreamReader` from a Container of bytes.
	// Any bytes preceding an initial sync word are ignored.
	template <typename T>
	static absl::optional<BitstreamReader<ArchType>> InitWithBytes(T bitstream);

	const std::vector<uint32_t>& words() { return words_; };

	// Returns an iterator that yields `ConfigurationPackets`
	// as read from the bitstream.
	iterator begin();
	iterator end();

       private:
	static std::array<uint8_t, 4> kSyncWord;

	std::vector<uint32_t> words_;
};

template <>
template <typename T>
std::optional<BitstreamReader<Series7>> BitstreamReader<Series7>::InitWithBytes(T bitstream) {
	// If this is really a Xilinx 7-Series bitstream, there will be a sync
	// word somewhere toward the beginning.
	auto sync_pos = std::search(bitstream.begin(), bitstream.end(),
	                            kSyncWord.begin(), kSyncWord.end());
	if (sync_pos == bitstream.end()) {
		return absl::optional<BitstreamReader<Series7>>();
	}
	sync_pos += kSyncWord.size();

	// Wrap the provided container in a span that strips off the preamble.
	absl::Span<typename T::value_type> bitstream_span(bitstream);
	auto config_packets =
	    bitstream_span.subspan(sync_pos - bitstream.begin());

	// Convert the bytes into 16-bit, big-endian words.
	auto big_endian_reader = make_big_endian_span<uint32_t>(config_packets);
	std::vector<uint32_t> words{big_endian_reader.begin(),
	                            big_endian_reader.end()};

	return BitstreamReader<Series7>(std::move(words));
}

template <typename ArchType>
std::array<uint8_t, 4> BitstreamReader<ArchType>::kSyncWord{0xAA, 0x99, 0x55, 0x66};

template <typename ArchType>
typename BitstreamReader<ArchType>::iterator BitstreamReader<ArchType>::begin() {
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
typename BitstreamReader<ArchType>::iterator& BitstreamReader<ArchType>::iterator::operator++() {
	do {
		auto new_result = ConfigurationPacket<typename ArchType::ConfRegType>::InitWithWords(
		    parse_result_.first, parse_result_.second.has_value()
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
bool BitstreamReader<ArchType>::iterator::operator==(const iterator& other) const {
	return words_ == other.words_;
}

template <typename ArchType>
bool BitstreamReader<ArchType>::iterator::operator!=(const iterator& other) const {
	return !(*this == other);
}

template <typename ArchType>
const typename BitstreamReader<ArchType>::value_type& BitstreamReader<ArchType>::iterator::operator*()
    const {
	return *(parse_result_.second);
}

template <typename ArchType>
const typename BitstreamReader<ArchType>::value_type* BitstreamReader<ArchType>::iterator::operator->()
    const {
	return parse_result_.second.operator->();
}
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_BITSTREAM_READER_H
