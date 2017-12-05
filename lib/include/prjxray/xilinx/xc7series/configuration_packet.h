#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_PACKET_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_PACKET_H

#include <cstdint>

#include <absl/types/optional.h>
#include <absl/types/span.h>
#include <prjxray/xilinx/xc7series/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class ConfigurationPacket {
 public:
	typedef std::pair<absl::Span<uint32_t>,
		          absl::optional<ConfigurationPacket>>
		ParseResult;

	enum Opcode {
		NOP = 0,
		Read = 1,
		Write = 2,
		/* reserved = 3 */
	};

	ConfigurationPacket(Opcode opcode, ConfigurationRegister address,
			    const absl::Span<uint32_t> &data)
		: opcode_(opcode), address_(address), data_(std::move(data)) {}

	// Attempt to read a configuration packet from a sequence of
	// 32-bit, big-endian words. If successful, returns the packet read and
	// a span containing any words remaining after the packet.  If a valid
	// header is found but there are insufficient words provided for the
	// complete packet, the original span<> is returned unchanged and no
	// packet is produced.  If no valid header is found, an empty span is
	// returned.
	static ParseResult InitWithWords(
			absl::Span<uint32_t> words,
			const ConfigurationPacket *previous_packet = nullptr);

	const Opcode opcode() const { return opcode_; }
	const ConfigurationRegister address() const { return address_; }
	const absl::Span<uint32_t> &data() const { return data_; }

 private:
	Opcode opcode_;
	ConfigurationRegister address_;
	absl::Span<uint32_t> data_;
};

std::ostream& operator<<(std::ostream& o, const ConfigurationPacket &packet);

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_PACKET_H
