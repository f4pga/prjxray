#ifndef PRJXRAY_LIB_XILINX_7SERIES_BITSTREAM_READER
#define PRJXRAY_LIB_XILINX_7SERIES_BITSTREAM_READER

#include <algorithm>
#include <memory>
#include <vector>

#include <absl/types/optional.h>
#include <absl/types/span.h>

#include <prjxray/big_endian_span.h>
#include <prjxray/xilinx_7series_configuration_packet.h>

namespace prjxray {

class Xilinx7SeriesBitstreamReader {
 public:
	using value_type = Xilinx7SeriesConfigurationPacket;

	class iterator
		: public std::iterator<std::input_iterator_tag, value_type> {
	 public:
		iterator& operator++();

		bool operator==(const iterator &other) const;
		bool operator!=(const iterator &other) const;

		const value_type& operator*() const;
		const value_type* operator->() const;

	 protected:
		explicit iterator(absl::Span<uint32_t> words);

	 private:
		friend Xilinx7SeriesBitstreamReader;

		Xilinx7SeriesConfigurationPacket::ParseResult parse_result_;
		absl::Span<uint32_t> words_;
	};

	// Construct a reader from a collection of 32-bit, big-endian words.
	// Assumes that any sync word has already been removed.
	Xilinx7SeriesBitstreamReader(std::vector<uint32_t> &&words);

	// Construct a `Xilinx7SeriesBitstreamReader` from a Container of bytes.
	// Any bytes preceding an initial sync word are ignored.
	template<typename T>
	static absl::optional<Xilinx7SeriesBitstreamReader> InitWithBytes(
			T &bitstream);

	// Returns an iterator that yields `Xilinx7SeriesConfigurationPackets`
	// as read from the bitstream.
	iterator begin();
	iterator end();
 private:
	static std::array<uint8_t, 4> kSyncWord;

	std::vector<uint32_t> words_;
};

template<typename T>
absl::optional<Xilinx7SeriesBitstreamReader>
Xilinx7SeriesBitstreamReader::InitWithBytes(T &bitstream) {
	// If this is really a Xilinx 7-Series bitstream, there will be a sync
	// word somewhere toward the beginning.
	auto sync_pos = std::search(bitstream.begin(), bitstream.end(),
				    kSyncWord.begin(), kSyncWord.end());
	if (sync_pos == bitstream.end()) {
		return absl::optional<Xilinx7SeriesBitstreamReader>();
	}
	sync_pos += kSyncWord.size();

	// Wrap the provided container in a span that strips off the preamble.
	absl::Span<typename T::value_type> bitstream_span(bitstream);
	auto config_packets = bitstream_span.subspan(sync_pos - bitstream.begin());

	// Convert the bytes into 32-bit, big-endian words.
	auto big_endian_reader = make_big_endian_span<uint32_t>(config_packets);
	std::vector<uint32_t> words{big_endian_reader.begin(),
				    big_endian_reader.end()};

	return Xilinx7SeriesBitstreamReader(std::move(words));
}

}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_7SERIES_BITSTREAM_READER
