# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
DATABASE_FILES = *.csv *.db *.json *.yaml *.fasm
TIMINGS_FILES = *.sdf
PART_DIRECTORIES = xc7*/

clean-artix7-db:
	rm -f $(addprefix artix7/,$(DATABASE_FILES))
	rm -f $(addprefix artix7/timings/,$(TIMINGS_FILES))
	rm -rf artix7/harness/
	rm -rf $(addprefix artix7/,$(PART_DIRECTORIES))

clean-kintex7-db:
	rm -f $(addprefix kintex7/,$(DATABASE_FILES))
	rm -f $(addprefix kintex7/timings/,$(TIMINGS_FILES))
	rm -rf kintex7/harness/
	rm -rf $(addprefix kintex7/,$(PART_DIRECTORIES))

clean-zynq7-db:
	rm -f $(addprefix zynq7/,$(DATABASE_FILES))
	rm -f $(addprefix zynq7/timings/,$(TIMINGS_FILES))
	rm -rf zynq7/harness/
	rm -rf $(addprefix zynq7/,$(PART_DIRECTORIES))

clean-spartan7-db:
	rm -f $(addprefix spartan7/,$(DATABASE_FILES))
	rm -f $(addprefix spartan7/timings/,$(TIMINGS_FILES))
	rm -rf spartan7/harness/
	rm -rf $(addprefix spartan7/,$(PART_DIRECTORIES))

clean-db: clean-artix7-db clean-kintex7-db clean-zynq7-db clean-spartan7-db
	@true

clean: clean-db
	@true

.PHONY: clean-artix7-db clean-kintex7-db clean-zynq7-db clean-spartan7-db clean-db clean

reset:
	git reset --hard

.PHONY: reset

update:
	git stash
	git fetch origin
	git merge origin/master
	git stash pop

.PHONY: update
