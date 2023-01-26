/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_CONFIGURATION_H_
#define PRJXRAY_LIB_XILINX_CONFIGURATION_H_

#include <map>
#include <type_traits>

#include <absl/types/span.h>

#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/frames.h>

namespace prjxray {
namespace xilinx {

template <typename ArchType>
class Configuration {
       public:
	using FrameMap = std::map<typename ArchType::FrameAddress,
	                          absl::Span<const uint32_t>>;

	struct PacketData {
		struct Frame {
			typename ArchType::FrameAddress address;
			std::vector<typename ArchType::FrameAddress> repeats;
			std::vector<uint32_t> data;
		};

		std::vector<Frame> frames;
	};

	// Returns a configuration, i.e. collection of frame addresses
	// and corresponding data from a collection of configuration packets.
	template <typename Collection>
	static absl::optional<Configuration<ArchType>> InitWithPackets(
	    const typename ArchType::Part& part,
	    Collection& packets);

	// Creates the complete configuration package which is later on
	// used by the bitstream writer to generate the bitstream file.
	// The pacakge forms a sequence suitable for Xilinx devices.
	// The programming sequence for Series-7 is taken from
	// https://www.kc8apf.net/2018/05/unpacking-xilinx-7-series-bitstreams-part-2/
	static void createConfigurationPackage(
	    typename ArchType::ConfigurationPackage& out_packets,
	    const PacketData& packet_data,
	    absl::optional<typename ArchType::Part>& part);

	// Returns the payload for a type 2 packet
	// which allows for bigger payload compared to type 1.
	static PacketData createType2ConfigurationPacketData(
	    const typename Frames<ArchType>::Frames2Data& frames,
	    absl::optional<typename ArchType::Part>& part,
	    bool compressed = false);

	Configuration(const typename ArchType::Part& part,
	              std::map<typename ArchType::FrameAddress,
	                       std::vector<uint32_t>>* frames)
	    : part_(part) {
		for (auto& frame : *frames) {
			frames_[frame.first] =
			    absl::Span<const uint32_t>(frame.second);
		}
	}

	Configuration(const typename ArchType::Part& part,
	              const FrameMap& frames)
	    : part_(part), frames_(std::move(frames)) {}

	const typename ArchType::Part& part() const { return part_; }
	const FrameMap& frames() const { return frames_; }
	void PrintFrameAddresses(FILE* fp);

       private:
	typename ArchType::Part part_;
	FrameMap frames_;
};

template <typename ArchType>
typename Configuration<ArchType>::PacketData
Configuration<ArchType>::createType2ConfigurationPacketData(
    const typename Frames<ArchType>::Frames2Data& frames,
    absl::optional<typename ArchType::Part>& part,
    bool compressed) {
	PacketData result;
	if (!compressed) {
		result.frames.push_back(typename PacketData::Frame{0U, {}, {}});
		std::vector<uint32_t>& packet_data = result.frames.back().data;
		// Certain configuration frames blocks are separated by Zero
		// Frames, i.e. frames with words with all zeroes. For Series-7,
		// US and US+ there zero frames separator consists of two
		// frames.
		static const int kZeroFramesSeparatorWords =
		    ArchType::words_per_frame * 2;
		for (auto& frame : frames) {
			std::copy(frame.second.begin(), frame.second.end(),
			          std::back_inserter(packet_data));

			auto next_address =
			    part->GetNextFrameAddress(frame.first);
			if (next_address &&
			    (next_address->block_type() !=
			         frame.first.block_type() ||
			     next_address->is_bottom_half_rows() !=
			         frame.first.is_bottom_half_rows() ||
			     next_address->row() != frame.first.row())) {
				packet_data.insert(packet_data.end(),
				                   kZeroFramesSeparatorWords,
				                   0);
			}
		}
		packet_data.insert(packet_data.end(), kZeroFramesSeparatorWords,
		                   0);
	} else {
		// First write takes priority.
		// FDRI writes must be padded with a trailing zero-frame.
		// FDRI writes followed by MFWRs must only write to a single
		//   frame.
		// Frame writes can be joined, so long as the frame written
		//   to with the trailing zero-frame has already been written
		//   to, or is meant to be a zero-frame.

		using Frame = typename PacketData::Frame;

		auto similar_address =
		    [](const typename ArchType::FrameAddress& a,
		       const typename ArchType::FrameAddress& b) -> bool {
			return a.block_type() == b.block_type() &&
			       a.is_bottom_half_rows() ==
			           b.is_bottom_half_rows() &&
			       a.row() == b.row();
		};

		for (const auto& frame : frames) {
			result.frames.push_back(
			    Frame{frame.first, {}, frame.second});
		}

		auto dedup = [](auto begin, auto end, auto compare,
		                auto merge) {
			while (begin != end) {
				auto mid = std::stable_partition(
				    begin + 1, end, [&](const Frame& f) {
					    return !compare(*begin, f);
				    });
				for (auto it = mid; it != end; ++it)
					merge(*begin, *it);
				end = mid;
				if (begin != end)
					++begin;
			}
			return begin;
		};

		auto can_merge = [&](const Frame& a, const Frame& b) -> bool {
			return b.repeats.empty() &&
			       similar_address(a.address, b.address) &&
			       a.data == b.data;
		};

		auto merge = [](Frame& dst, Frame& src) {
			dst.repeats.push_back(src.address);
		};

		result.frames.erase(
		    dedup(result.frames.begin(), result.frames.end(), can_merge,
		          merge),
		    result.frames.end());

		std::set<typename ArchType::FrameAddress> deduped_frames;

		auto zero_frames_between =
		    [&](const typename ArchType::FrameAddress& a,
		        const typename ArchType::FrameAddress& b,
		        size_t max) -> size_t {
			if (a >= b)
				return 0;
			auto next = part->GetNextFrameAddress(a);
			for (size_t result = 1;
			     result <= max && next && *next <= b &&
			     deduped_frames.count(*next) > 0U;
			     ++result,
			            next = part->GetNextFrameAddress(*next)) {
				if (*next == b)
					return result;
			}
			return 0;
		};

		// Merge contiguous frames
		Frame* previous = nullptr;
		absl::optional<typename ArchType::FrameAddress>
		    previous_next_address;
		for (auto& frame : result.frames) {
			if (!frame.repeats.empty()) {
				if (previous)
					deduped_frames.insert(
					    previous->repeats.begin(),
					    previous->repeats.end());
				previous = &frame;
			} else {
				if (previous_next_address) {
					const size_t between =
					    zero_frames_between(
					        *previous_next_address,
					        frame.address, 2U);
					if (between > 0U) {
						previous->data.resize(
						    previous->data.size() +
						        (ArchType::
						             words_per_frame *
						         between),
						    0U);
						previous_next_address =
						    frame.address;
					}
				}
				if (previous_next_address &&
				    *previous_next_address == frame.address) {
					previous->data.insert(
					    previous->data.end(),
					    frame.data.begin(),
					    frame.data.end());
					frame.data.clear();
				} else {
					if (previous)
						deduped_frames.insert(
						    previous->repeats.begin(),
						    previous->repeats.end());
					previous = &frame;
				}
			}
			if (previous)
				previous_next_address =
				    part->GetNextFrameAddress(frame.address);
		}

		result.frames.erase(
		    std::remove_if(
		        result.frames.begin(), result.frames.end(),
		        [](const Frame& frame) { return frame.data.empty(); }),
		    result.frames.end());

		for (auto& frame : result.frames) {
			if (frame.repeats.empty()) {
				frame.data.resize(frame.data.size() +
				                      ArchType::words_per_frame,
				                  0U);
			}
		}
	}
	return result;
}

template <>
template <typename Collection>
absl::optional<Configuration<Spartan6>>
Configuration<Spartan6>::InitWithPackets(const typename Spartan6::Part& part,
                                         Collection& packets) {
	using ArchType = Spartan6;
	// Registers that can be directly written to.
	uint32_t command_register = 0;
	uint32_t frame_address_register = 0;
	uint32_t mask_register = 0;
	__attribute__((unused)) uint32_t ctl1_register = 0;

	// Internal state machine for writes.
	bool start_new_write = false;
	typename ArchType::FrameAddress current_frame_address = 0;

	Configuration<ArchType>::FrameMap frames;
	for (auto packet : packets) {
		if (packet.opcode() !=
		    ConfigurationPacket<
		        typename ArchType::ConfRegType>::Opcode::Write) {
			continue;
		}

		switch (packet.address()) {
			case ArchType::ConfRegType::MASK:
				if (packet.data().size() < 1)
					continue;
				mask_register = packet.data()[0];
				break;
			case ArchType::ConfRegType::CTL:
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
				// for the next FDRI.
				if (command_register == 0x1) {
					start_new_write = true;
				}
				break;
			case ArchType::ConfRegType::IDCODE: {
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
			case ArchType::ConfRegType::FAR_MAJ: {
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
			case ArchType::ConfRegType::FAR_MIN:
				// This really should be a one-word write.
				if (packet.data().size() < 1)
					continue;

				frame_address_register |=
				    packet.data()[0] & 0x3FF;

				break;
			case ArchType::ConfRegType::FDRI: {
				if (start_new_write) {
					current_frame_address =
					    frame_address_register;
					start_new_write = false;
				}

				// Spartan6 frames are 65-words long.  Writes
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

template <typename ArchType>
template <typename Collection>
absl::optional<Configuration<ArchType>>
Configuration<ArchType>::InitWithPackets(const typename ArchType::Part& part,
                                         Collection& packets) {
	// Registers that can be directly written to.
	uint32_t command_register = 0;
	uint32_t frame_address_register = 0;
	uint32_t mask_register = 0;
	uint32_t ctl1_register = 0;

	// Internal state machine for writes.
	bool start_new_write = false;
	bool start_dup_write = false;
	typename ArchType::FrameAddress last_write_frame_address = 0;
	typename ArchType::FrameAddress current_frame_address = 0;

	Configuration<ArchType>::FrameMap frames;
	for (auto packet : packets) {
		if (packet.opcode() !=
		    ConfigurationPacket<
		        typename ArchType::ConfRegType>::Opcode::Write) {
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
				} else if (command_register == 0x2) {
					start_dup_write = true;
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
				// register is loaded with a new value.  As we
				// only care about WCFG and MFWR commands, just
				// check that here.  CTRL1 is completely
				// undocumented but looking at generated
				// bitstreams, bit 21 is used when per-frame CRC
				// is enabled. Setting this bit seems to inhibit
				// the re-execution of CMD during a FAR write.
				// In practice, this is used so FAR writes can
				// be added in the bitstream to show progress
				// markers without impacting the actual write
				// operation.
				if (bit_field_get(ctl1_register, 21, 21) == 0) {
					if (command_register == 0x1) {
						start_new_write = true;
					} else if (command_register == 0x2) {
						start_dup_write = true;
					}
				}
				break;
			case ArchType::ConfRegType::FDRI: {
				if (start_new_write) {
					last_write_frame_address =
					    current_frame_address =
					        frame_address_register;
					start_new_write = false;
				}

				// Number of words in configuration frames
				// depend on the architecture.  Writes to this
				// register can be multiples of that number to
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
						ii += 2 *
						      ArchType::words_per_frame;
					}
					current_frame_address = *next_address;
				}
				break;
			}
			case ArchType::ConfRegType::MFWR: {
				if (start_dup_write) {
					current_frame_address =
					    frame_address_register;
					start_dup_write = false;
					frames[current_frame_address] =
					    frames[last_write_frame_address];
				}
			} break;
			default:
				break;
		}
	}

	return Configuration(part, frames);
}

template <typename ArchType>
void Configuration<ArchType>::PrintFrameAddresses(FILE* fp) {
	fprintf(fp, "Frame addresses in bitstream: ");
	for (auto frame = frames_.begin(); frame != frames_.end(); ++frame) {
		fprintf(fp, "%08X", (int)frame->first);
		if (std::next(frame) != frames_.end()) {
			fprintf(fp, " ");
		} else {
			fprintf(fp, "\n");
		}
	}
}

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_CONFIGURATION_H_
