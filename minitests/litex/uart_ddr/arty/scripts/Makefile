# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
litex/litex/tools/litex_client.py:
	git clone https://github.com/enjoy-digital/litex.git
	cd litex && git checkout 3350d33 && cd ../

test_dram: litex/litex/tools/litex_client.py
	./test_sdram.py
