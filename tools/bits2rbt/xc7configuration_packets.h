#ifndef CONFIGURATION_PACKETS_H_
#define CONFIGURATION_PACKETS_H_
#include <array>
#include <map>
#include <memory>
#include <unordered_map>

#include "ecc.h"
#include "header.h"

class ConfigurationPackets {
       public:
	ConfigurationPackets(const std::string& arch);
	static const std::unordered_map<std::string, size_t>
	    words_in_architecture;
	static std::shared_ptr<ConfigurationPackets> InitFromFile(
	    const std::string& file,
	    const std::string& arch);
	void AddAuxData(const std::string& file);
	void WriteBits(std::ostream& out);
	void SetBits(std::ifstream& ifs);

       private:
	using ConfigurationFrame = std::pair<uint32_t, std::vector<uint32_t>>;
	using ConfigurationFrames = std::map<uint32_t, std::vector<uint32_t>>;
	// Refer to UG470 page 109 for address of configuration registers and
	// commands
	const uint32_t kCmdWrite = 0x30008000;
	const uint32_t kFdriWrite = 0x30004000;
	const uint32_t kFarWrite = 0x30002000;
	const uint32_t kCrcWrite = 0x30000000;
	const uint32_t kNop = 0x20000000;
	const uint32_t kFarReg = 0x1;
	const uint32_t kFdriReg = 0x2;
	const uint32_t kCmdReg = 0x4;
	const uint32_t kWcfgCmd = 0x1;
	// Writing the RCRC(0x7) command in type 1 packet with 1 word to the CMD
	// register (0x30008001)
	const std::array<uint32_t, 2> kRCrcCmd = {{0x30008001, 0x7}};
	size_t words_per_frame_;
	std::string architecture_;
	ConfigurationFrames configuration_data_packets_;
	std::vector<uint32_t> fpga_configuration_head_;
	std::vector<uint32_t> fpga_configuration_tail_;
	std::unique_ptr<Header> header_;
	ECC ecc_;

	void InitializeConfigurationData(const std::string& line);
	void InitializeFpgaConfigurationHead(const std::string& line);
	void InitializeFpgaConfigurationTail(const std::string& line);
	void InitializeHeader(const std::string& line);
	uint32_t GetCRC(ConfigurationFrames::const_iterator frame_citr,
	                bool is_new_row = false) const;
	uint32_t GetFpgaConfigurationCRC() const;
	void UpdateECCs();
	void SetBit(const std::string& line);
	void WriteConfiguration(std::ostream& out);
	void WriteFpgaConfiguration(std::ostream& out,
	                            const std::vector<uint32_t>& vect);
	void WritePacket(std::ostream& out,
	                 ConfigurationFrames::const_iterator frame_citr) const;
	bool IsDifferentRow(
	    ConfigurationFrames::const_iterator frame_citr1,
	    ConfigurationFrames::const_iterator frame_citr2) const;
	void Line2Vector(const std::string& line, std::vector<uint32_t>& vect);
};
#endif  // CONFIGURATION_PACKETS_H_
