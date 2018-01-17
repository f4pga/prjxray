#include <prjxray/xilinx/xc7series/configuration_packetizer.h>

#include <absl/types/span.h>
#include <prjxray/xilinx/xc7series/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

ConfigurationPacketizer::ConfigurationPacketizer(const Configuration& config)
    : config_(config) {}

ConfigurationPacketizer::iterator ConfigurationPacketizer::begin() const {
	return iterator(&config_.part(), config_.frames().begin(),
	                config_.frames().end());
}

ConfigurationPacketizer::iterator ConfigurationPacketizer::end() const {
	return iterator(&config_.part(), config_.frames().end(),
	                config_.frames().end());
}

ConfigurationPacketizer::iterator::iterator(
    const Part* part,
    Configuration::FrameMap::const_iterator begin,
    Configuration::FrameMap::const_iterator end)
    : part_(part),
      state_(begin != end ? State::Start : State::Finished),
      frame_cur_(begin),
      frame_end_(end) {
	this->operator++();
}

const ConfigurationPacket& ConfigurationPacketizer::iterator::operator*()
    const {
	return *packet_;
}

const ConfigurationPacket* ConfigurationPacketizer::iterator::operator->()
    const {
	return &(*packet_);
}

bool ConfigurationPacketizer::iterator::operator==(
    const ConfigurationPacketizer::iterator& other) const {
	return state_ == other.state_ && frame_cur_ == other.frame_cur_;
}

bool ConfigurationPacketizer::iterator::operator!=(
    const ConfigurationPacketizer::iterator& other) const {
	return !(*this == other);
}

ConfigurationPacketizer::iterator& ConfigurationPacketizer::iterator::
operator++() {
	// Frames are accessed via an indirect addressing scheme using the FAR
	// and FDRI registers.  Writes begin with writing the target frame
	// address to FAR and then the frame data is written to FDRI.  The
	// following state machine primarily follows that flow:
	// Start -> FrameAddressWritten -> FrameDataWritten -> Start....
	// When the last frame within a row is written, 2 full frames (202
	// words) of zero padding need to be written after the frame data.
	switch (state_) {
		case State::FrameDataWritten: {
			// If this is the last address in this row (i.e. the
			// next valid address known by the part is in a
			// different row, half, or bus type), start a zero fill.
			// Otherwise, increment the frame iterator and fall
			// through to Start.
			auto& this_address = frame_cur_->first;
			auto next_address =
			    part_->GetNextFrameAddress(frame_cur_->first);
			if (next_address &&
			    (next_address->block_type() !=
			         this_address.block_type() ||
			     next_address->is_bottom_half_rows() !=
			         this_address.is_bottom_half_rows() ||
			     next_address->row() != this_address.row())) {
				zero_pad_packets_to_write_ = 202;
				// Type 0 frames aren't documented in UG470.  In
				// practice, they are used to zero pad in the
				// bitstream.
				packet_ = ConfigurationPacket(
				    0, ConfigurationPacket::Opcode::NOP,
				    ConfigurationRegister::CRC, {});
				state_ = State::ZeroPadWritten;
				break;
			}

			++frame_cur_;
		}
		case State::Start:
			if (frame_cur_ == frame_end_) {
				state_ = State::Finished;
				frame_address_.reset();
				packet_.reset();
				return *this;
			}

			frame_address_ = frame_cur_->first;
			packet_ = ConfigurationPacket(
			    1, ConfigurationPacket::Opcode::Write,
			    ConfigurationRegister::FAR,
			    absl::Span<uint32_t>(&frame_address_.value(), 1));
			state_ = State::FrameAddressWritten;
			break;
		case State::FrameAddressWritten:
			packet_ = ConfigurationPacket(
			    1, ConfigurationPacket::Opcode::Write,
			    ConfigurationRegister::FDRI, frame_cur_->second);
			state_ = State::FrameDataWritten;
			break;
		case State::ZeroPadWritten:
			if (--zero_pad_packets_to_write_ == 1) {
				++frame_cur_;
				state_ = State::Start;
			}
			break;
		case State::Finished:
			break;
	}

	return *this;
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
