# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N := 10
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database.txt: $(SPECIMENS_OK)
	cat $(addsuffix /segdata.txt,$(SPECIMENS)) | ../../tools/segmatch > database.new
	mv database.new database.txt

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf $(SPECIMENS)

.PHONY: clean

