
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
    segbits_rioi3 \
    segbits_riob33 \
    segbits_hclk_ioi3 \

ifneq (${XRAY_DATABASE}, zynq7)
DB_SIMPLE += segbits_lioi3 segbits_liob33
endif

BLOCK_RAM_EXTRA_FOR=\
      mask_bram \
      segbits_bram
BLOCK_RAM_EXTRA_DB_FILES=\
      $(addsuffix .block_ram.db,$(addsuffix _l,$(BLOCK_RAM_EXTRA_FOR)) $(addsuffix _r,$(BLOCK_RAM_EXTRA_FOR)))


DB_FILES=$(sort $(addsuffix .origin_info.db,$(DB_SIMPLE)) $(addsuffix .db,$(DB_SIMPLE)) $(BLOCK_RAM_EXTRA_DB_FILES))
DB_FILES_PATH=$(addprefix $(XRAY_DATABASE_DIR)/$(XRAY_DATABASE)/,$(DB_FILES))

check:
	@mkdir -p build
	@rm -f build/existing.txt
	@for DB_FILE in $(sort $(notdir $(wildcard $(XRAY_DATABASE_DIR)/$(XRAY_DATABASE)/*.db))); do \
		echo $$DB_FILE >> build/existing.txt; \
	done
	@rm -f build/tocreate.txt
	@for DB_FILE in $(sort $(DB_FILES)); do \
		echo $$DB_FILE >> build/tocreate.txt; \
	done
	diff -u build/existing.txt build/tocreate.txt

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

pushdb: $(DB_FILES_PATH)
	@true

run:
	$(MAKE) clean
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: pushdb clean run
