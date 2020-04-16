/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
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
