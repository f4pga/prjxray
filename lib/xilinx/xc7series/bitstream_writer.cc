/*
 * TODO
 * -Finish type 1/2 support
 * -Review sample bitstream padding. What are they for?
 */
#include <prjxray/xilinx/xc7series/bitstream_writer.h>

#include <prjxray/bit_ops.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

// Per UG470 pg 80: Bus Width Auto Detection
std::array<uint32_t, 6> BitstreamWriter::header_{
    0xFFFFFFFF, 0x000000BB, 0x11220044, 0xFFFFFFFF, 0xFFFFFFFF, 0xAA995566};

/**************************************************
 * BitstreamWriter::BitstreamWriter
 *************************************************/

BitstreamWriter::BitstreamWriter(const packets_t& packets)
    : packets_(packets) {}

/**************************************************
 *
 *************************************************/

BitstreamWriter::packet_iterator BitstreamWriter::iterator::packet_begin() {
	// itr_packets = packets.begin();
	const ConfigurationPacket& packet = *itr_packets_;

	return BitstreamWriter::packet_iterator(
	    &packet, BitstreamWriter::packet_iterator::STATE_HEADER,
	    packet.data().begin());
}

BitstreamWriter::packet_iterator BitstreamWriter::iterator::packet_end() {
	const ConfigurationPacket& packet = *itr_packets_;

	return BitstreamWriter::packet_iterator(
	    &packet, BitstreamWriter::packet_iterator::STATE_END,
	    // Essentially ignored
	    packet.data().end());
}

BitstreamWriter::packet_iterator::packet_iterator(
    const ConfigurationPacket* packet,
    state_t state,
    data_iterator_t itr_data)
    : state_(state), itr_data_(itr_data), packet_(packet) {}

BitstreamWriter::packet_iterator& BitstreamWriter::packet_iterator::
operator++() {
	if (state_ == STATE_HEADER) {
		itr_data_ = packet_->data().begin();
		if (itr_data_ == packet_->data().end()) {
			state_ = STATE_END;
		} else {
			state_ = STATE_DATA;
		}
	} else if (state_ == STATE_DATA) {
		/// Advance. data must be valid while not at end
		itr_data_++;
		// Reached this end of this packet?
		if (itr_data_ == packet_->data().end()) {
			state_ = STATE_END;
		}
	}
	return *this;
}

bool BitstreamWriter::packet_iterator::operator==(
    const packet_iterator& other) const {
	return state_ == other.state_ && itr_data_ == other.itr_data_;
}

bool BitstreamWriter::packet_iterator::operator!=(
    const packet_iterator& other) const {
	return !(*this == other);
}

uint32_t packet2header(const ConfigurationPacket& packet) {
	uint32_t ret = 0;

	ret = bit_field_set(ret, 31, 29, packet.header_type());

	switch (packet.header_type()) {
		case 0x0:
			// Bitstreams are 0 padded sometimes, essentially making
			// a type 0 frame Ignore the other fields for now
			break;
		case 0x1: {
			// Table 5-20: Type 1 Packet Header Format
			ret = bit_field_set(ret, 28, 27, packet.opcode());
			ret = bit_field_set(ret, 26, 13, packet.address());
			ret = bit_field_set(ret, 10, 0, packet.data().length());
			break;
		}
		case 0x2: {
			// Table 5-22: Type 2 Packet Header
			// Note address is from previous type 1 header
			ret = bit_field_set(ret, 28, 27, packet.opcode());
			ret = bit_field_set(ret, 26, 0, packet.data().length());
			break;
		}
		default:
			break;
	}

	return ret;
}

const BitstreamWriter::itr_value_type BitstreamWriter::packet_iterator::
operator*() const {
	if (state_ == STATE_HEADER) {
		return packet2header(*packet_);
	} else if (state_ == STATE_DATA) {
		return *itr_data_;
	}
	return 0;  // XXX: assert or something?
}

const BitstreamWriter::itr_value_type BitstreamWriter::packet_iterator::
operator->() const {
	return *(*this);
}

/**************************************************
 * BitstreamWriter::iterator
 *************************************************/

BitstreamWriter::iterator BitstreamWriter::begin() {
	packets_t::const_iterator itr_packets = packets_.begin();
	absl::optional<packet_iterator> op_packet_itr;

	// May have no packets
	if (itr_packets != packets_.end()) {
		// op_packet_itr = packet_begin();
		// FIXME: de-duplicate this
		const ConfigurationPacket& packet = *itr_packets;
		packet_iterator packet_itr =
		    packet_iterator(&packet, packet_iterator::STATE_HEADER,
		                    packet.data().begin());
		op_packet_itr = packet_itr;
	}
	return iterator(header_.begin(), packets_, itr_packets, op_packet_itr);
}

BitstreamWriter::iterator BitstreamWriter::end() {
	return iterator(header_.end(), packets_, packets_.end(),
	                absl::optional<packet_iterator>());
}

BitstreamWriter::iterator::iterator(header_t::iterator itr_header,
                                    const packets_t& packets,
                                    packets_t::const_iterator itr_packets,
                                    absl::optional<packet_iterator> itr_packet)
    : itr_header_(itr_header),
      packets_(packets),
      itr_packets_(itr_packets),
      op_itr_packet_(itr_packet) {}

BitstreamWriter::iterator& BitstreamWriter::iterator::operator++() {
	// Still generating header?
	if (itr_header_ != header_.end()) {
		itr_header_++;
		// Finished header?
		// Will advance to initialized itr_packets value
		// XXX: maybe should just overwrite here
		if (itr_header_ == header_.end()) {
			itr_packets_ = packets_.begin();
			if (itr_packets_ != packets_.end()) {
				op_itr_packet_ = packet_begin();
			}
		}
		// Then somewhere in packets
	} else {
		// We are either at end() in which case this operation is
		// invalid Or there is a packet in progress packet in progress?
		// Advance it
		++(*op_itr_packet_);
		// Done with this packet?
		if (*op_itr_packet_ == packet_end()) {
			itr_packets_++;
			if (itr_packets_ == packets_.end()) {
				// we are at the very end
				// invalidate data to be neat
				op_itr_packet_.reset();
			} else {
				op_itr_packet_ = packet_begin();
			}
		}
	}
	return *this;
}

bool BitstreamWriter::iterator::operator==(const iterator& other) const {
	return itr_header_ == other.itr_header_ &&
	       itr_packets_ == other.itr_packets_ &&
	       op_itr_packet_ == other.op_itr_packet_;
}

bool BitstreamWriter::iterator::operator!=(const iterator& other) const {
	return !(*this == other);
}

const BitstreamWriter::itr_value_type BitstreamWriter::iterator::operator*()
    const {
	if (itr_header_ != header_.end()) {
		return *itr_header_;
	} else {
		// Iterating over packets, get data from current packet position
		return *(*op_itr_packet_);
	}
}

const BitstreamWriter::itr_value_type BitstreamWriter::iterator::operator->()
    const {
	return *(*this);
}

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray
