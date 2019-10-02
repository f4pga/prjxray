#include <prjxray/xilinx/configuration_packet.h>

#include <iomanip>
#include <iostream>
#include <ostream>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {

template <>
std::pair<absl::Span<uint32_t>,
          absl::optional<ConfigurationPacket<Series7ConfigurationRegister>>>
ConfigurationPacket<Series7ConfigurationRegister>::InitWithWords(
    absl::Span<uint32_t> words,
    const ConfigurationPacket<Series7ConfigurationRegister>* previous_packet) {
	using ConfigurationRegister = Series7ConfigurationRegister;
	// Need at least one 32-bit word to have a valid packet header.
	if (words.size() < 1)
		return {words, {}};

	uint32_t header_type = bit_field_get(words[0], 31, 29);
	switch (header_type) {
		case NONE:
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
		case TYPE1: {
			Opcode opcode = static_cast<Opcode>(
			    bit_field_get(words[0], 28, 27));
			ConfigurationRegister address =
			    static_cast<ConfigurationRegister>(
			        bit_field_get(words[0], 26, 13));
			uint32_t data_word_count =
			    bit_field_get(words[0], 10, 0);

			// If the full packet has not been received, return as
			// though no valid packet was found.
			if (data_word_count > words.size() - 1) {
				return {words, {}};
			}

			return {words.subspan(data_word_count + 1),
			        {{header_type, opcode, address,
			          words.subspan(1, data_word_count)}}};
		}
		case TYPE2: {
			absl::optional<ConfigurationPacket> packet;
			Opcode opcode = static_cast<Opcode>(
			    bit_field_get(words[0], 28, 27));
			uint32_t data_word_count =
			    bit_field_get(words[0], 26, 0);

			// If the full packet has not been received, return as
			// though no valid packet was found.
			if (data_word_count > words.size() - 1) {
				return {words, {}};
			}

			if (previous_packet) {
				packet = ConfigurationPacket(
				    header_type, opcode,
				    previous_packet->address(),
				    words.subspan(1, data_word_count));
			}

			return {words.subspan(data_word_count + 1), packet};
		}
		default:
			return {{}, {}};
	}
}

template <class ConfigRegType>
std::ostream& operator<<(std::ostream& o,
                         const ConfigurationPacket<ConfigRegType>& packet) {
	if (packet.header_type() == 0x0) {
		return o << "[Zero-pad]" << std::endl;
	}

	switch (packet.opcode()) {
		case ConfigurationPacket<ConfigRegType>::Opcode::NOP:
			o << "[NOP]" << std::endl;
			break;
		case ConfigurationPacket<ConfigRegType>::Opcode::Read:
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
		case ConfigurationPacket<ConfigRegType>::Opcode::Write:
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

template std::ostream& operator<<(
    std::ostream&,
    const ConfigurationPacket<Series7ConfigurationRegister>&);
}  // namespace xilinx
}  // namespace prjxray
