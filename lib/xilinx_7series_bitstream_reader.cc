#include <prjxray/xilinx_7series_bitstream_reader.h>

namespace prjxray {

std::array<uint8_t, 4> Xilinx7SeriesBitstreamReader::kSyncWord{
	0xAA, 0x99, 0x55, 0x66};

Xilinx7SeriesBitstreamReader::Xilinx7SeriesBitstreamReader(
		std::vector<uint32_t> &&words)
	: words_(std::move(words)) {}

Xilinx7SeriesBitstreamReader::iterator Xilinx7SeriesBitstreamReader::begin() {
	return iterator(absl::MakeSpan(words_));
}

Xilinx7SeriesBitstreamReader::iterator Xilinx7SeriesBitstreamReader::end() {
	return iterator({});
}

Xilinx7SeriesBitstreamReader::iterator::iterator(absl::Span<uint32_t> words) {
	parse_result_.first = words;
	parse_result_.second = {};
	++(*this);
}

Xilinx7SeriesBitstreamReader::iterator&
Xilinx7SeriesBitstreamReader::iterator::operator++() {
	do {
		auto new_result = Xilinx7SeriesConfigurationPacket::InitWithWords(
					parse_result_.first,
					parse_result_.second.has_value() ?
						parse_result_.second.operator->() :
						nullptr);

		// If the a valid header is being found but there are
		// insufficient words to yield a packet, consider it the end.
		if (new_result.first == parse_result_.first) {
			words_ = absl::Span<uint32_t>();
			break;
		}

		words_ = parse_result_.first;
		parse_result_ = new_result;
	} while (!parse_result_.first.empty() &&
		 !parse_result_.second);

	if (!parse_result_.second) {
		words_ = absl::Span<uint32_t>();
	}

	return *this;
}

bool Xilinx7SeriesBitstreamReader::iterator::operator==(const iterator &other) const {
	return words_ == other.words_;
}

bool Xilinx7SeriesBitstreamReader::iterator::operator!=(const iterator &other) const {
	return !(*this == other);
}

const Xilinx7SeriesBitstreamReader::value_type&
Xilinx7SeriesBitstreamReader::iterator::operator*() const {
	return *(parse_result_.second);
}

const Xilinx7SeriesBitstreamReader::value_type*
Xilinx7SeriesBitstreamReader::iterator::operator->() const {
	return parse_result_.second.operator->();
}


}  // namespace prjxray
