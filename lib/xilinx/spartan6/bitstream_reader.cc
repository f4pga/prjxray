#include <prjxray/xilinx/spartan6/bitstream_reader.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

std::array<uint8_t, 4> BitstreamReader::kSyncWord{0xAA, 0x99, 0x55, 0x66};

BitstreamReader::BitstreamReader(std::vector<uint32_t>&& words)
    : words_(std::move(words)) {}

BitstreamReader::iterator BitstreamReader::begin() {
	return iterator(absl::MakeSpan(words_));
}

BitstreamReader::iterator BitstreamReader::end() {
	return iterator({});
}

BitstreamReader::iterator::iterator(absl::Span<uint32_t> words) {
	parse_result_.first = words;
	parse_result_.second = {};
	++(*this);
}

BitstreamReader::iterator& BitstreamReader::iterator::operator++() {
	do {
		auto new_result = ConfigurationPacket::InitWithWords(
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

bool BitstreamReader::iterator::operator==(const iterator& other) const {
	return words_ == other.words_;
}

bool BitstreamReader::iterator::operator!=(const iterator& other) const {
	return !(*this == other);
}

const BitstreamReader::value_type& BitstreamReader::iterator::operator*()
    const {
	return *(parse_result_.second);
}

const BitstreamReader::value_type* BitstreamReader::iterator::operator->()
    const {
	return parse_result_.second.operator->();
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray
