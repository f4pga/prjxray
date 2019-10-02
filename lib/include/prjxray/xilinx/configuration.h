#ifndef PRJXRAY_LIB_XILINX_CONFIGURATION_H_
#define PRJXRAY_LIB_XILINX_CONFIGURATION_H_

#include <map>
#include <optional>
#include <type_traits>

#include <absl/types/span.h>

#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/frames.h>
#include <prjxray/xilinx/architectures.h>

namespace prjxray {
namespace xilinx {

template <typename ArchType>
class Configuration {
       public:
	using FrameMap = std::map<typename ArchType::FrameAddress, absl::Span<const uint32_t>>;
	using PacketData = std::vector<uint32_t>;

	template <typename Collection>
	static std::optional<Configuration<ArchType>> InitWithPackets(
				const typename ArchType::Part& part,
				Collection& packets);

	static void createConfigurationPackage(typename ArchType::ConfigurationPackage& out_packets,
                                const PacketData& packet_data,
                                absl::optional<typename ArchType::Part>& part);

	static PacketData createType2ConfigurationPacketData(const typename Frames<ArchType>::Frames2Data& frames,
                                              absl::optional<typename ArchType::Part>& part);

	Configuration(const typename ArchType::Part& part,
	              std::map<typename ArchType::FrameAddress, std::vector<uint32_t>>* frames)
	    : part_(part) {
		for (auto& frame : *frames) {
			frames_[frame.first] =
			    absl::Span<const uint32_t>(frame.second);
		}
	}

	Configuration(const typename ArchType::Part& part, const FrameMap& frames)
	    : part_(part), frames_(std::move(frames)) {}

	const typename ArchType::Part& part() const { return part_; }
	const FrameMap& frames() const { return frames_; }

       private:
	typename ArchType::Part part_;
	FrameMap frames_;
};

template <>
template <typename Collection>
std::optional<Configuration<Series7>> Configuration<Series7>::InitWithPackets(
    const typename Series7::Part& part,
    Collection& packets) {
	using ArchType = Series7;
	// Registers that can be directly written to.
	uint32_t command_register = 0;
	uint32_t frame_address_register = 0;
	uint32_t mask_register = 0;
	uint32_t ctl1_register = 0;

	// Internal state machine for writes.
	bool start_new_write = false;
	typename ArchType::FrameAddress current_frame_address = 0;

	Configuration<ArchType>::FrameMap frames;
	for (auto packet : packets) {
		if (packet.opcode() != ConfigurationPacket<typename ArchType::ConfRegType>::Opcode::Write) {
			continue;
		}

		switch (packet.address()) {
			case ArchType::ConfRegType::MASK:
				if (packet.data().size() < 1)
					continue;
				mask_register = packet.data()[0];
				break;
			case ArchType::ConfRegType::CTL1:
				if (packet.data().size() < 1)
					continue;
				ctl1_register =
				    packet.data()[0] & mask_register;
				break;
			case ArchType::ConfRegType::CMD:
				if (packet.data().size() < 1)
					continue;
				command_register = packet.data()[0];
				// Writes to CMD trigger an immediate action. In
				// the case of WCFG, that is just setting a flag
				// for the next FDIR.
				if (command_register == 0x1) {
					start_new_write = true;
				}
				break;
			case ArchType::ConfRegType::IDCODE:
				// This really should be a one-word write.
				if (packet.data().size() < 1)
					continue;

				// If the IDCODE doesn't match our expected
				// part, consider the bitstream invalid.
				if (packet.data()[0] != part.idcode()) {
					return {};
				}
				break;
			case ArchType::ConfRegType::FAR:
				// This really should be a one-word write.
				if (packet.data().size() < 1)
					continue;
				frame_address_register = packet.data()[0];

				// Per UG470, the command present in the CMD
				// register is executed each time the FAR
				// register is laoded with a new value.  As we
				// only care about WCFG commands, just check
				// that here.  CTRL1 is completely undocumented
				// but looking at generated bitstreams, bit 21
				// is used when per-frame CRC is enabled.
				// Setting this bit seems to inhibit the
				// re-execution of CMD during a FAR write.  In
				// practice, this is used so FAR writes can be
				// added in the bitstream to show progress
				// markers without impacting the actual write
				// operation.
				if (bit_field_get(ctl1_register, 21, 21) == 0 &&
				    command_register == 0x1) {
					start_new_write = true;
				}
				break;
			case ArchType::ConfRegType::FDRI: {
				if (start_new_write) {
					current_frame_address =
					    frame_address_register;
					start_new_write = false;
				}

				// 7-series frames are 101-words long.  Writes
				// to this register can be multiples of that to
				// do auto-incrementing block writes.
				for (size_t ii = 0; ii < packet.data().size();
				     ii += ArchType::words_per_frame) {
					frames[current_frame_address] =
					    packet.data().subspan(
					        ii, ArchType::words_per_frame);

					auto next_address =
					    part.GetNextFrameAddress(
					        current_frame_address);
					if (!next_address)
						break;

					// Bitstreams appear to have 2 frames of
					// padding between rows.
					if (next_address &&
					    (next_address->block_type() !=
					         current_frame_address
					             .block_type() ||
					     next_address
					             ->is_bottom_half_rows() !=
					         current_frame_address
					             .is_bottom_half_rows() ||
					     next_address->row() !=
					         current_frame_address.row())) {
						ii += 2 * ArchType::words_per_frame;
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

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_CONFIGURATION_H_
