
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_UTILS_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_UTILS_H_

#include <prjxray/xilinx/xc7series/configuration.h>
#include <prjxray/xilinx/xc7series/configuration_packet.h>
#include <prjxray/xilinx/xc7series/frames.h>
#include <prjxray/xilinx/xc7series/part.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {
using PacketData = std::vector<uint32_t>;
using BitstreamHeader = std::vector<uint8_t>;
using ConfigurationPackage = std::vector<std::unique_ptr<ConfigurationPacket>>;

PacketData createType2ConfigurationPacketData(const Frames::Frames2Data& frames,
                                              absl::optional<Part>& part);
void createConfigurationPackage(ConfigurationPackage& out_packets,
                                const PacketData& packet_data,
                                absl::optional<Part>& part);
BitstreamHeader createBitistreamHeader(const std::string& part_name,
                                       const std::string& frames_file_name,
                                       const std::string& generator_name);
int writeBitstream(const ConfigurationPackage& packets,
                   const std::string& part_name,
                   const std::string& frames_file,
                   const std::string& generator_name,
                   const std::string& output_file);
}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_UTILS_H_
