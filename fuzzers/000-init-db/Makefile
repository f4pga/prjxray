
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

DB_SIMPLE=$(addprefix mask_,$(MASKS)) $(addprefix ppips_,$(PPIPS)) $(addprefix segbits_,$(SEGBITS))

# Extra (segbits|mask)_bram_(l|r).block_ram.db files
# FIXME: Are these things also needed for the DSP blocks?
BLOCK_RAM_EXTRA_FOR=mask_bram segbits_bram
BLOCK_RAM_EXTRA_DB_FILES=$(addsuffix .block_ram.db,$(addsuffix _l,$(BLOCK_RAM_EXTRA_FOR)) $(addsuffix _r,$(BLOCK_RAM_EXTRA_FOR)))

DB_FILES=$(sort $(addsuffix _l.db,$(DB_SIMPLE)) $(addsuffix _r.db,$(DB_SIMPLE)) $(BLOCK_RAM_EXTRA_DB_FILES))
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
