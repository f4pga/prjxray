#ifndef HEADER_H_
#define HEADER_H_
#include <absl/strings/string_view.h>
#include <iostream>
#include <string>
#include <vector>
#include <cstdint>

class Header {
       public:
	Header(const std::string& line,
	       std::vector<uint32_t>& fpga_config_packets);
	void Write(std::ostream& out);

       private:
	std::string design_name_;
	std::string part_;
	std::string date_;
	uint32_t no_bits_;

	std::string GetTLVHeaderValue(absl::string_view& str_view);
	uint32_t GetWord(absl::string_view& str_view);
	size_t GetTLVHeaderLength(absl::string_view& str_view);
	size_t GetByteAndAdvance(absl::string_view& str_view);
	std::string GetDate();
	std::string GetArchitecture();
};
#endif  // HEADER_H_
