/*
 * Takes in a collection of ConfigurationPacket and writes them to specified
 * file This includes the following: -Bus auto detection -Sync Word -FPGA
 * configuration
 */
#ifndef PRJXRAY_LIB_XILINX_BITSTREAM_WRITER_H
#define PRJXRAY_LIB_XILINX_BITSTREAM_WRITER_H

#include <algorithm>
#include <memory>
#include <vector>

#include <absl/types/optional.h>
#include <absl/types/span.h>

#include <prjxray/big_endian_span.h>
#include <prjxray/xilinx/configuration_packet.h>

namespace prjxray {
namespace xilinx {

template <typename ArchType>
class BitstreamWriter {
       public:
	typedef std::vector<uint32_t> header_t;
	typedef std::vector<std::unique_ptr<ConfigurationPacket<typename ArchType::ConfRegType>>> packets_t;
	typedef std::vector<uint8_t> BitstreamHeader;
	// Only defined if a packet exists
	typedef absl::optional<absl::Span<const uint32_t>> op_data_t;
	typedef absl::Span<const uint32_t>::iterator data_iterator_t;
	using itr_value_type = uint32_t;

	class packet_iterator
	    : public std::iterator<std::input_iterator_tag, itr_value_type> {
	       public:
		packet_iterator& operator++();

		bool operator==(const packet_iterator& other) const;
		bool operator!=(const packet_iterator& other) const;

		const itr_value_type operator*() const;
		const itr_value_type operator->() const;

		typedef enum {
			STATE_HEADER = 1,
			STATE_DATA = 2,
			STATE_END = 3,
		} state_t;

	       protected:
		explicit packet_iterator(const ConfigurationPacket<typename ArchType::ConfRegType>* packet,
		                         state_t state,
		                         data_iterator_t itr_data);

	       private:
		friend iterator;
		friend BitstreamWriter;

		// Data iterators
		// First over the fixed header, then the configuration data
		state_t state_;
		// Over packet.data()
		data_iterator_t itr_data_;

		const ConfigurationPacket<typename ArchType::ConfRegType>* packet_;
	};

	class iterator
	    : public std::iterator<std::input_iterator_tag, itr_value_type> {
	       public:
		iterator& operator++();

		bool operator==(const iterator& other) const;
		bool operator!=(const iterator& other) const;

		const itr_value_type operator*() const;
		const itr_value_type operator->() const;

		packet_iterator packet_begin();
		packet_iterator packet_end();

	       protected:
		explicit iterator(
		    header_t::iterator itr_header,
		    const packets_t& packets,
		    typename packets_t::const_iterator itr_packets,
		    absl::optional<packet_iterator> op_itr_packet);

	       private:
		friend BitstreamWriter;
		// Data iterators
		// First over the fixed header, then the configuration data
		header_t::iterator itr_header_;
		const packets_t& packets_;
		typename packets_t::const_iterator itr_packets_;
		absl::optional<packet_iterator> op_itr_packet_;
	};

	BitstreamWriter(const packets_t& packets)
		: packets_(packets) {}

	int writeBitstream(const typename ArchType::ConfigurationPackage& packets,
                   const std::string& part_name,
                   const std::string& frames_file,
                   const std::string& generator_name,
                   const std::string& output_file);
	iterator begin();
	iterator end();

       private:
	static header_t header_;
	const packets_t& packets_;

	BitstreamHeader create_header(const std::string& part_name,
                                      const std::string& frames_file_name,
                                      const std::string& generator_name);
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_BITSTREAM_WRITER_H
