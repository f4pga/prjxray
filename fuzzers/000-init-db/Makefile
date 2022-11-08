# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

MASKS=\
      bram \
      clbll \
      clblm \
      dsp \
      hclk \

PPIPS=\
      bram \
      bram_int_interface \
      clbll \
      clblm \
      dsp \
      hclk \
      int \

SEGBITS=\
      bram \
      clbll \
      clblm \
      dsp \
      hclk \
      int \

SEGBITS_R=\
      clk_bufg_top \
      clk_bufg_bot \
      $(SEGBITS)

SEGBITS_L=\
      $(SEGBITS)

DB_SIMPLE_LR=$(addprefix mask_,$(MASKS)) $(addprefix ppips_,$(PPIPS))
DB_SIMPLE_L=$(addprefix segbits_,$(SEGBITS_L))
DB_SIMPLE_R=$(addprefix segbits_,$(SEGBITS_R))
DB_SIMPLE=\
    $(addsuffix _l, $(DB_SIMPLE_LR) $(DB_SIMPLE_L)) \
    $(addsuffix _r, $(DB_SIMPLE_LR) $(DB_SIMPLE_R)) \
    segbits_cmt_top_l_upper_t \
    segbits_cmt_top_r_upper_t \
    segbits_cmt_top_l_lower_b \
    segbits_cmt_top_r_lower_b \
    segbits_rioi3 \
    segbits_riob33 \
    segbits_riob18 \
    segbits_hclk_cmt \
    segbits_hclk_ioi3 \

DB_SIMPLE += segbits_lioi3 segbits_liob33

BLOCK_RAM_EXTRA_FOR=\
      mask_bram \
      segbits_bram
BLOCK_RAM_EXTRA_DB_FILES=\
      $(addsuffix .block_ram.db,$(addsuffix _l,$(BLOCK_RAM_EXTRA_FOR)) $(addsuffix _r,$(BLOCK_RAM_EXTRA_FOR)))


DB_FILES=$(sort $(addsuffix .origin_info.db,$(DB_SIMPLE)) $(addsuffix .db,$(DB_SIMPLE)) $(BLOCK_RAM_EXTRA_DB_FILES))
DB_FILES_PATH=$(addprefix $(XRAY_DATABASE_DIR)/$(XRAY_DATABASE)/,$(DB_FILES))

BUILD_DIR = build_${XRAY_PART}

check:
	@mkdir -p $(BUILD_DIR)
	@rm -f $(BUILD_DIR)/existing.txt
	@for DB_FILE in $(sort $(notdir $(wildcard $(XRAY_DATABASE_DIR)/$(XRAY_DATABASE)/*.db))); do \
		echo $$DB_FILE >> $(BUILD_DIR)/existing.txt; \
	done
	@rm -f $(BUILD_DIR)/tocreate.txt
	@for DB_FILE in $(sort $(DB_FILES)); do \
		echo $$DB_FILE >> $(BUILD_DIR)/tocreate.txt; \
	done
	diff -u $(BUILD_DIR)/existing.txt $(BUILD_DIR)/tocreate.txt

status:
	@echo $(DB_FILES_PATH)
	@for DB_FILE in $(DB_FILES_PATH); do \
		echo -n "$$(basename $$DB_FILE) "; \
		if [ -e "$$DB_FILE" ]; then \
			echo -n "Exists! - "; \
		else \
			echo -n "Missing! - "; \
		fi; \
		echo "$$DB_FILE"; \
	done

$(DB_FILES_PATH):
	touch $@

${XRAY_FAMILY_DIR}/${XRAY_PART}:
	mkdir -p ${XRAY_FAMILY_DIR}/${XRAY_PART}

${XRAY_FAMILY_DIR}/${XRAY_FABRIC}:
	mkdir -p ${XRAY_FAMILY_DIR}/${XRAY_FABRIC}

pushdb: $(DB_FILES_PATH) ${XRAY_FAMILY_DIR}/${XRAY_PART} ${XRAY_FAMILY_DIR}/${XRAY_FABRIC}
	@true

run:
	rm -rf $(BUILD_DIR) run.${XRAY_PART}.ok
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf build_* run.*.ok

.PHONY: pushdb clean run
