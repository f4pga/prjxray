#include <prjxray/xilinx/frames.h>
#include <prjxray/xilinx/xc7series/ecc.h>

namespace prjxray {
namespace xilinx {
template <>
void Frames<Series7>::updateECC(typename Frames<Series7>::FrameData& data) {
	xc7series::updateECC(data);
}

template <>
void Frames<UltraScale>::updateECC(
    typename Frames<UltraScale>::FrameData& data) {
	xc7series::updateECC(data);
}

template <>
void Frames<UltraScalePlus>::updateECC(
    typename Frames<UltraScalePlus>::FrameData& data) {
	xc7series::updateECC(data);
}

// Spartan6 doesn't have ECC
template <>
void Frames<Spartan6>::updateECC(typename Frames<Spartan6>::FrameData& data) {}

}  // namespace xilinx
}  // namespace prjxray
