
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_UTILS_H_
#define PRJXRAY_LIB_XILINX_XC7SERIES_UTILS_H_

#include <prjxray/xilinx/spartan6/configuration.h>
#include <prjxray/xilinx/spartan6/configuration_packet.h>
#include <prjxray/xilinx/spartan6/frames.h>
#include <prjxray/xilinx/spartan6/part.h>

namespace prjxray {
namespace xilinx {
namespace spartan6 {
using PacketData = std::vector<uint32_t>;
using BitstreamHeader = std::vector<uint8_t>;
using ConfigurationPackage = std::vector<std::unique_ptr<ConfigurationPacket>>;

// Returns the payload for a type 2 packet.
// Type 2 packets can have the payload length of more than the 11 bits available
// for type 1 packets.
PacketData createType2ConfigurationPacketData(const Frames::Frames2Data& frames,
                                              absl::optional<Part>& part);

// Creates the complete configuration package that is
// then used by the bitstream writer to generate the bitstream file. The package
// forms a sequence suitable for xilinx 7-series devices. The programming
// sequence is taken from
// https://www.kc8apf.net/2018/05/unpacking-xilinx-7-series-bitstreams-part-2/
void createConfigurationPackage(ConfigurationPackage& out_packets,
                                const PacketData& packet_data,
                                absl::optional<Part>& part);

// Creates a Xilinx bit header which is mostly a
// Tag-Length-Value(TLV) format documented here:
// http://www.fpga-faq.com/FAQ_Pages/0026_Tell_me_about_bit_files.htm
BitstreamHeader createBitistreamHeader(const std::string& part_name,
                                       const std::string& frames_file_name,
                                       const std::string& generator_name);

// Writies out the complete bitstream for a 7-series
// Xilinx FPGA based on the Configuration Package which holds the complete
// programming sequence.
int writeBitstream(const ConfigurationPackage& packets,
                   const std::string& part_name,
                   const std::string& frames_file,
                   const std::string& generator_name,
                   const std::string& output_file);
}  // namespace spartan6
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_UTILS_H_
