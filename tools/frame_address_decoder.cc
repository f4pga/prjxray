/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <fstream>
#include <iomanip>
#include <iostream>

#include <prjxray/xilinx/xc7series/frame_address.h>

namespace xc7series = prjxray::xilinx::xc7series;

void frame_address_decode(std::istream* input_stream) {
	for (uint32_t frame_address_raw;
	     (*input_stream) >> std::setbase(0) >> frame_address_raw;) {
		xc7series::FrameAddress frame_address(frame_address_raw);
		std::cout << "[" << std::hex << std::showbase << std::setw(10)
		          << frame_address_raw << "] "
		          << (frame_address.is_bottom_half_rows() ? "BOTTOM"
		                                                  : "TOP")
		          << " Row=" << std::setw(2) << std::dec
		          << static_cast<unsigned int>(frame_address.row())
		          << " Column=" << std::setw(2) << std::dec
		          << frame_address.column() << " Minor=" << std::setw(2)
		          << std::dec
		          << static_cast<unsigned int>(frame_address.minor())
		          << " Type=" << frame_address.block_type()
		          << std::endl;
	}
}

int main(int argc, char* argv[]) {
	if (argc > 1) {
		std::ifstream file_stream(argv[1]);
		if (file_stream) {
			frame_address_decode(&file_stream);
			return 0;
		}
	}

	frame_address_decode(&std::cin);

	return 0;
}
