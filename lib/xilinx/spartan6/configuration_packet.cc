#include <prjxray/xilinx/spartan6/configuration_packet.h>

#include <iomanip>
#include <iostream>
#include <ostream>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

std::pair<absl::Span<uint32_t>, absl::optional<ConfigurationPacket>>
ConfigurationPacket::InitWithWords(absl::Span<uint32_t> words,
                                   const ConfigurationPacket* previous_packet) {
	// Need at least one 32-bit word to have a valid packet header.
	if (words.size() < 1)
		return {words, {}};

	uint32_t header_type = bit_field_get(words[0], 15, 13);
	switch (header_type) {
		case 0x0:
			// Type 0 is emitted at the end of a configuration row
			// when BITSTREAM.GENERAL.DEBUGBITSTREAM is set to YES.
			// These seem to be padding that are interepreted as
			// NOPs.  Since Type 0 packets don't exist according to
			// UG470 and they seem to be zero-filled, just consume
			// the bytes without generating a packet.
			return {words.subspan(1),
			        {{header_type,
			          Opcode::NOP,
			          ConfigurationRegister::CRC,
			          {}}}};
		case 0x1: {
			Opcode opcode = static_cast<Opcode>(
			    bit_field_get(words[0], 12, 11));
			ConfigurationRegister address =
			    static_cast<ConfigurationRegister>(
			        bit_field_get(words[0], 10, 5));
			uint32_t data_word_count =
			    bit_field_get(words[0], 4, 0);

			// If the full packet has not been received, return as
			// though no valid packet was found.
			if (data_word_count > words.size() - 1) {
				return {words, {}};
			}

			return {words.subspan(data_word_count + 1),
			        {{header_type, opcode, address,
			          words.subspan(1, data_word_count)}}};
		}
		case 0x2: {
			absl::optional<ConfigurationPacket> packet;
			Opcode opcode = static_cast<Opcode>(
			    bit_field_get(words[0], 12, 11));
			ConfigurationRegister address =
			    static_cast<ConfigurationRegister>(
			        bit_field_get(words[0], 10, 5));
			// Type 2 packets according to UG380 consist of
			// a header word followed by 2 WCD (Word Count Data)
			// words
			uint32_t data_word_count = (words[1] << 16) | words[2];

			// If the full packet has not been received, return as
			// though no valid packet was found.
			if (data_word_count > words.size() - 1) {
				return {words, {}};
			}

			// Create a packet that contains as many data words
			// as specified in the WCD packets, but omit them
			// in the configuration packet along with the header
			// FIXME Figure out why we need the extra 2 words
			packet = ConfigurationPacket(
			    header_type, opcode, address,
			    words.subspan(3, data_word_count + 2));

			return {words.subspan(data_word_count + 3), packet};
		}
		default:
			return {{}, {}};
	}
}

std::ostream& operator<<(std::ostream& o, const ConfigurationPacket& packet) {
	if (packet.header_type() == 0x0) {
		return o << "[Zero-pad]" << std::endl;
	}

	switch (packet.opcode()) {
		case ConfigurationPacket::Opcode::NOP:
			o << "[NOP]" << std::endl;
			break;
		case ConfigurationPacket::Opcode::Read:
			o << "[Read Type=";
			o << packet.header_type();
			o << " Address=";
			o << std::setw(2) << std::hex;
			o << static_cast<int>(packet.address());
			o << " Length=";
			o << std::setw(10) << std::dec << packet.data().size();
			o << " Reg=\"" << packet.address() << "\"";
			o << "]" << std::endl;
			break;
		case ConfigurationPacket::Opcode::Write:
			o << "[Write Type=";
			o << packet.header_type();
			o << " Address=";
			o << std::setw(2) << std::hex;
			o << static_cast<int>(packet.address());
			o << " Length=";
			o << std::setw(10) << std::dec << packet.data().size();
			o << " Reg=\"" << packet.address() << "\"";
			o << "]" << std::endl;
			o << "Data in hex:" << std::endl;

			for (size_t ii = 0; ii < packet.data().size(); ++ii) {
				o << std::setw(8) << std::hex;
				o << packet.data()[ii] << " ";

				if ((ii + 1) % 4 == 0) {
					o << std::endl;
				}
			}
			if (packet.data().size() % 4 != 0) {
				o << std::endl;
			}
			break;
		default:
			o << "[Invalid Opcode]" << std::endl;
	}

	return o;
}

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray
