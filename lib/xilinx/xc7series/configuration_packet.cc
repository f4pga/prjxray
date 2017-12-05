#include <prjxray/xilinx/xc7series/configuration_packet.h>

#include <ostream>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

std::pair<absl::Span<uint32_t>, absl::optional<ConfigurationPacket>>
ConfigurationPacket::InitWithWords(absl::Span<uint32_t> words,
				   const ConfigurationPacket *previous_packet) {
	// Need at least one 32-bit word to have a valid packet header.
	if (words.size() < 1) return  {words, {}};

	uint32_t header_type = bit_field_get(words[0], 31, 29);
	switch (header_type) {
	case 0b001: {
		Opcode opcode = static_cast<Opcode>(
				bit_field_get(words[0], 28, 27));
		uint32_t address = bit_field_get(words[0], 26, 13);
		uint32_t data_word_count = bit_field_get(words[0], 10, 0);

		// If the full packet has not been received, return as though
		// no valid packet was found.
		if (data_word_count > words.size() - 1) {
			return {words, {}};
		}

		return {words.subspan(data_word_count+1),
			{{opcode, address, words.subspan(1, data_word_count)}}};
	}
	case 0b010: {
		absl::optional<ConfigurationPacket> packet;
		Opcode opcode = static_cast<Opcode>(
				bit_field_get(words[0], 28, 27));
		uint32_t data_word_count = bit_field_get(words[0], 26, 0);

		// If the full packet has not been received, return as though
		// no valid packet was found.
		if (data_word_count > words.size() - 1) {
			return {words, {}};
		}

		if (previous_packet) {
			packet = ConfigurationPacket(
					opcode, previous_packet->address(),
					words.subspan(1, data_word_count));
		}

		return {words.subspan(data_word_count + 1), packet};
	}
	default:
		return {{}, {}};
	}
}

std::ostream& operator<<(std::ostream& o, const ConfigurationPacket &packet) {
	switch (packet.opcode()) {
		case ConfigurationPacket::Opcode::NOP:
			return o << "[NOP]" << std::endl;
		case ConfigurationPacket::Opcode::Read:
			return o << "[Read Address=" << packet.address()
				 << " Length=" << packet.data().size() <<
				 "]" << std::endl;
		case ConfigurationPacket::Opcode::Write:
			return o << "[Write Address=" << packet.address()
				 << " Length=" << packet.data().size() <<
				 "]" << std::endl;
		default:
			return o << "[Invalid Opcode]" << std::endl;
	}
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
