#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_PACKETIZER_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_PACKETIZER_H_

#include <absl/types/optional.h>
#include <prjxray/xilinx/xc7series/configuration.h>
#include <prjxray/xilinx/xc7series/configuration_packet.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class ConfigurationPacketizer {
       public:
	class iterator
	    : std::iterator<std::input_iterator_tag, ConfigurationPacket> {
	       public:
		iterator(const Part* part,
		         Configuration::FrameMap::const_iterator begin,
		         Configuration::FrameMap::const_iterator end);

		iterator& operator++();

		bool operator==(const iterator& other) const;
		bool operator!=(const iterator& other) const;

		const ConfigurationPacket& operator*() const;
		const ConfigurationPacket* operator->() const;

	       private:
		friend class ConfigurationPacketizer;

		enum class State {
			Start,
			FrameAddressWritten,
			FrameDataWritten,
			ZeroPadWritten,
			Finished,
		};

		const Part* part_;
		State state_;
		Configuration::FrameMap::const_iterator frame_cur_;
		Configuration::FrameMap::const_iterator frame_end_;
		absl::optional<uint32_t> frame_address_;
		absl::optional<ConfigurationPacket> packet_;
		int zero_pad_packets_to_write_;
	};

	ConfigurationPacketizer(const Configuration& config);

	iterator begin() const;
	iterator end() const;

       private:
	const Configuration& config_;
};

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_PACKETIZER_H_
