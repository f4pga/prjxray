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
class UltraScale;
class UltraScalePlus;

class Architecture {
       public:
	using Container = absl::variant<Series7, UltraScale, UltraScalePlus>;
	Architecture(const std::string& name) : name_(name) {}
	const std::string& name() const { return name_; }
	virtual ~Architecture() {}

       private:
	const std::string name_;
};

class Series7 : public Architecture {
       public:
	using ConfRegType = Series7ConfigurationRegister;
	using Part = xc7series::Part;
	using ConfigurationPackage =
	    std::vector<std::unique_ptr<ConfigurationPacket<ConfRegType>>>;
	using FrameAddress = xc7series::FrameAddress;
	using WordType = uint32_t;
	Series7() : Architecture("Series7") {}
	Series7(const std::string& name) : Architecture(name) {}
	static constexpr int words_per_frame = 101;
};

class UltraScalePlus : public Series7 {
       public:
	UltraScalePlus() : Series7("UltraScalePlus") {}
	static constexpr int words_per_frame = 93;
};

class UltraScale : public Series7 {
       public:
	UltraScale() : Series7("UltraScale") {}
	static constexpr int words_per_frame = 123;
};

class ArchitectureFactory {
       public:
	static Architecture::Container create_architecture(
	    const std::string& arch) {
		if (arch == "Series7") {
			return Series7();
		} else if (arch == "UltraScale") {
			return UltraScale();
		} else if (arch == "UltraScalePlus") {
			return UltraScalePlus();
		} else {
			return Architecture::Container();
		}
	}
};

}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_ARCHITECTURES_H_
