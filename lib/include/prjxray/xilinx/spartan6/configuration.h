#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_H_

#include <map>

#include <absl/types/span.h>
#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/spartan6/bitstream_reader.h>
#include <prjxray/xilinx/spartan6/configuration_packet.h>
#include <prjxray/xilinx/spartan6/frame_address.h>
#include <prjxray/xilinx/spartan6/part.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {

class Configuration {
       public:
	using FrameMap = std::map<FrameAddress, absl::Span<const uint32_t>>;

	template <typename Collection>
	static absl::optional<Configuration> InitWithPackets(
	    const Part& part,
	    Collection& packets);

	Configuration(const Part& part,
	              std::map<FrameAddress, std::vector<uint32_t>>* frames)
	    : part_(part) {
		for (auto& frame : *frames) {
			frames_[frame.first] =
			    absl::Span<const uint32_t>(frame.second);
		}
	}

	Configuration(const Part& part, const FrameMap& frames)
	    : part_(part), frames_(std::move(frames)) {}

	const Part& part() const { return part_; }
	const FrameMap& frames() const { return frames_; }

       private:
	static constexpr int kWordsPerFrame = 65;

	Part part_;
	FrameMap frames_;
};

template <typename Collection>
absl::optional<Configuration> Configuration::InitWithPackets(
    const Part& part,
    Collection& packets) {
	// Registers that can be directly written to.
	uint32_t command_register = 0;
	uint32_t frame_address_register = 0;
	uint32_t mask_register = 0;
	__attribute__((unused)) uint32_t ctl1_register = 0;

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
				if (packet.data().size() < 1)
					continue;
				mask_register = packet.data()[0];
				break;
			case ConfigurationRegister::CTL:
				if (packet.data().size() < 1)
					continue;
				ctl1_register =
				    packet.data()[0] & mask_register;
				break;
			case ConfigurationRegister::CMD:
				if (packet.data().size() < 1)
					continue;
				command_register = packet.data()[0];
				// Writes to CMD trigger an immediate action. In
				// the case of WCFG, that is just setting a flag
				// for the next FDRI.
				if (command_register == 0x1) {
					start_new_write = true;
				}
				break;
			case ConfigurationRegister::IDCODE: {
				// This really should be a two-word write.
				if (packet.data().size() < 2)
					continue;

				// If the IDCODE doesn't match our expected
				// part, consider the bitstream invalid.
				uint32_t idcode = (packet.data()[0] << 16) |
				                  (packet.data()[1]);
				if (idcode != part.idcode()) {
					return {};
				}
				break;
			}
			// UG380 describes the frame addressing scheme where two
			// words for FAR_MAJ update FAR_MAJ anda FAR_MIN -
			// FAR_MAJ comes first
			case ConfigurationRegister::FAR_MAJ: {
				size_t packet_size = packet.data().size();
				assert(packet_size < 3);
				if (packet_size < 1) {
					continue;
				} else if (packet_size < 2) {
					frame_address_register =
					    (packet.data()[0] & 0xFFFF) << 16;
				} else {
					frame_address_register =
					    ((packet.data()[0] & 0xFFFF)
					     << 16) |
					    (packet.data()[1] & 0xFFFF);
				}
				break;
			}
			case ConfigurationRegister::FAR_MIN:
				// This really should be a one-word write.
				if (packet.data().size() < 1)
					continue;

				frame_address_register |=
				    packet.data()[0] & 0x3FF;

				break;
			case ConfigurationRegister::FDRI: {
				if (start_new_write) {
					current_frame_address =
					    frame_address_register;
					start_new_write = false;
				}

				// Spartan6 frames are 65-words long.  Writes
				// to this register can be multiples of that to
				// do auto-incrementing block writes.

				for (size_t ii = 0; ii < packet.data().size();
				     ii += kWordsPerFrame) {
					frames[current_frame_address] =
					    packet.data().subspan(
					        ii, kWordsPerFrame);

					auto next_address =
					    part.GetNextFrameAddress(
					        current_frame_address);
					if (!next_address)
						break;

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

}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_H_
