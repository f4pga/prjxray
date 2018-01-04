#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_H_

#include <map>

#include <absl/types/span.h>
#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/xc7series/bitstream_reader.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <prjxray/xilinx/xc7series/part.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class Configuration {
 public:
	using FrameMap = std::map<FrameAddress,
				  absl::Span<uint32_t>>;

	template<typename Collection>
	static absl::optional<Configuration> InitWithPackets(
			const Part& part, Collection &packets);

	Configuration(const Part& part, const FrameMap &frames)
		: part_(part), frames_(std::move(frames)) {}

	const Part& part() const { return part_; }
	const FrameMap& frames() const { return frames_; }

 private:
	static constexpr int kWordsPerFrame = 101;

	Part part_;
	FrameMap frames_;
};

template<typename Collection>
absl::optional<Configuration> Configuration::InitWithPackets(
		const Part& part, Collection &packets) {
	// Registers that can be directly written to.
	uint32_t command_register = 0;
	uint32_t frame_address_register = 0;
	uint32_t mask_register = 0;
	uint32_t ctl1_register = 0;

	// Internal state machine for writes.
	bool start_new_write = false;
	FrameAddress current_frame_address = 0;

	Configuration::FrameMap frames;
	for (auto packet : packets) {
		if (packet.opcode() != ConfigurationPacket::Opcode::Write) {
			continue;
		}

		switch (packet.address()) {
		case ConfigurationRegister::MASK:
			if (packet.data().size() < 1) continue;
			mask_register = packet.data()[0];
			break;
		case ConfigurationRegister::CTL1:
			if (packet.data().size() < 1) continue;
			ctl1_register = packet.data()[0] & mask_register;
			break;
		case ConfigurationRegister::CMD:
			if (packet.data().size() < 1) continue;
			command_register = packet.data()[0];
			// Writes to CMD trigger an immediate action.  In the case of
			// WCFG, that is just setting a flag for the next FDIR.
			if (command_register == 0x1) {
				start_new_write = true;
			}
			break;
		case ConfigurationRegister::IDCODE:
			// This really should be a one-word write.
			if (packet.data().size() < 1) continue;

			// If the IDCODE doesn't match our expected part,
			// consider the bitstream invalid.
			if (packet.data()[0] != part.idcode()) {
				return {};
			}
			break;
		case ConfigurationRegister::FAR:
			// This really should be a one-word write.
			if (packet.data().size() < 1) continue;
			frame_address_register = packet.data()[0];

			// Per UG470, the command present in the CMD register
			// is executed each time the FAR register is laoded
			// with a new value.  As we only care about WCFG
			// commands, just check that here.  CTRL1 is completely
			// undocumented but looking at generated bitstreams, bit 21
			// is used when per-frame CRC is enabled.  Setting this
			// bit seems to inhibit the re-execution of CMD during a
			// FAR write.  In practice, this is used so FAR writes
			// can be added in the bitstream to show progress
			// markers without impacting the actual write
			// operation.
			if (bit_field_get(ctl1_register, 21, 21) == 0 &&
			    command_register == 0x1) {
				start_new_write = true;
			}
			break;
		case ConfigurationRegister::FDRI: {
			if (start_new_write) {
				current_frame_address = frame_address_register;
				start_new_write = false;
			}

			// 7-series frames are 101-words long.  Writes to this
			// register can be multiples of that to do
			// auto-incrementing block writes.
			for (size_t ii = 0;
			     ii < packet.data().size();
			     ii += kWordsPerFrame) {
				frames[current_frame_address] =
					packet.data().subspan(
							ii, kWordsPerFrame);

				auto next_address = part.GetNextFrameAddress(
						current_frame_address);
				if (!next_address) break;

				// Bitstreams appear to have 2 frames of
				// padding between rows.
				if (next_address->row_address() !=
				    current_frame_address.row_address()) {
					ii += 2 * kWordsPerFrame;
				}
				current_frame_address = *next_address;
			}
			break;
		}
		default:
			break;
		}
	}

	return Configuration(part, frames);
}


}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_H_
