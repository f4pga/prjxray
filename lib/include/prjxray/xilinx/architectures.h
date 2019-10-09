#ifndef PRJXRAY_LIB_XILINX_ARCHITECTURES_H_
#define PRJXRAY_LIB_XILINX_ARCHITECTURES_H_

#include <absl/types/variant.h>
#include <memory>
#include <vector>

#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/configuration_register.h>
#include <prjxray/xilinx/xc7series/frame_address.h>
#include <prjxray/xilinx/xc7series/part.h>

namespace prjxray {
namespace xilinx {

class Series7;

class Architecture {
       public:
	using Container = absl::variant<Series7>;
	virtual const std::string& name() const = 0;
};

class Series7 : public Architecture {
       public:
	using ConfRegType = Series7ConfigurationRegister;
	using Part = xc7series::Part;
	using ConfigurationPackage =
	    std::vector<std::unique_ptr<ConfigurationPacket<ConfRegType>>>;
	using FrameAddress = xc7series::FrameAddress;
	using WordType = uint32_t;
	Series7() : name_("Series7") {}
	const std::string& name() const override { return name_; }
	static constexpr int words_per_frame = 101;

       private:
	std::string name_;
};

class ArchitectureFactory {
       public:
	static Architecture::Container create_architecture(
	    const std::string& arch) {
		if (arch == "Series7") {
			return Series7();
		} else {
			return Architecture::Container();
		}
	}
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_ARCHITECTURES_H_
