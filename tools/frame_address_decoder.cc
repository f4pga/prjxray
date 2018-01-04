#include <fstream>
#include <iomanip>
#include <iostream>

#include <prjxray/xilinx/xc7series/frame_address.h>

namespace xc7series = prjxray::xilinx::xc7series;

int main(int argc, char *argv[]) {
	std::istream * input_stream = &std::cin;
	if (argc > 1) {
		auto file_stream = std::ifstream(argv[1]);
		if (file_stream) {
			input_stream = &file_stream;
		}
	}

	for (uint32_t frame_address_raw;
	     (*input_stream) >> std::setbase(0) >> frame_address_raw;
	     ) {
		xc7series::FrameAddress frame_address(frame_address_raw);
		std::cout << "["
			  << std::hex << std::showbase << std::setw(10)
			  << frame_address_raw
			  << "] "
			  << (frame_address.is_bottom_half_rows() ?
				     "BOTTOM" : "TOP")
			  << " Row="
			  << std::setw(2) << std::dec
			  << static_cast<unsigned int>(frame_address.row_address())
			  << " Column="
			  << std::setw(2) << std::dec
			  << frame_address.column_address()
			  << " Minor="
			  << std::setw(2) << std::dec
			  << static_cast<unsigned int>(frame_address.minor_address())
			  << " Type="
			  << frame_address.block_type()
			  << std::endl;
	}

	return 0;
}
