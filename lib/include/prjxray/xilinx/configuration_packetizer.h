#ifndef PRJXRAY_LIB_XILINX_CONFIGURATION_PACKETIZER_H_
#define PRJXRAY_LIB_XILINX_CONFIGURATION_PACKETIZER_H_

#include <absl/types/optional.h>
#include <absl/types/span.h>
#include <prjxray/xilinx/configuration.h>

namespace prjxray {
namespace xilinx {

template <typename ArchType>
class ConfigurationPacketizer {
       public:
	class iterator
	    : std::iterator<
	          std::input_iterator_tag,
	          ConfigurationPacket<typename ArchType::ConfRegType>> {
	       public:
		iterator(
		    const typename ArchType::Part* part,
		    typename Configuration<ArchType>::FrameMap::const_iterator
		        begin,
		    typename Configuration<ArchType>::FrameMap::const_iterator
		        end);

		iterator& operator++();

		bool operator==(const iterator& other) const;
		bool operator!=(const iterator& other) const;

		const ConfigurationPacket<typename ArchType::ConfRegType>&
		operator*() const;
		const ConfigurationPacket<typename ArchType::ConfRegType>*
		operator->() const;

	       private:
		friend class ConfigurationPacketizer;

		enum class State {
			Start,
			FrameAddressWritten,
			FrameDataWritten,
			ZeroPadWritten,
			Finished,
		};

		const typename ArchType::Part* part_;
		State state_;
		typename Configuration<ArchType>::FrameMap::const_iterator
		    frame_cur_;
		typename Configuration<ArchType>::FrameMap::const_iterator
		    frame_end_;
		absl::optional<uint32_t> frame_address_;
		absl::optional<
		    ConfigurationPacket<typename ArchType::ConfRegType>>
		    packet_;
		int zero_pad_packets_to_write_;
	};

	ConfigurationPacketizer(const Configuration<ArchType>& config);

	iterator begin() const;
	iterator end() const;

       private:
	const Configuration<ArchType>& config_;
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_CONFIGURATION_PACKETIZER_H_
