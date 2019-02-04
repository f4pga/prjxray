# Developer options for quicker runs
# Run algorithm, but only a small number of iterations
QUICK=N
# Skip metadata steps like tile and part generation
# Ex: FUZZONLY=N: 30 min, FUZZONLY=Y: 6 min
FUZZONLY=N
# 074 fuzzer isn't changed often and is slow
# Allow building without it
BITONLY=N

all:

define fuzzer
all: $(1)/run.ok
clean::
	$$(MAKE) -C $(1) clean
$(1)/run.ok: $(addsuffix /run.ok,$(2))
	$$(MAKE) -C $(1) run
endef

$(eval $(call fuzzer,000-init-db,))

ifneq ($(FUZZONLY),Y)
$(eval $(call fuzzer,001-part-yaml,000-init-db))
$(eval $(call fuzzer,005-tilegrid,001-part-yaml))
else
all:: 005-tilegrid/run.ok
	touch 005-tilegrid/run.ok
endif

$(eval $(call fuzzer,010-clb-lutinit,005-tilegrid))
$(eval $(call fuzzer,011-clb-ffconfig,005-tilegrid))
$(eval $(call fuzzer,012-clb-n5ffmux,005-tilegrid))
$(eval $(call fuzzer,013-clb-ncy0,005-tilegrid))
$(eval $(call fuzzer,014-clb-ffsrcemux,005-tilegrid))
$(eval $(call fuzzer,015-clb-nffmux,005-tilegrid))
$(eval $(call fuzzer,016-clb-noutmux,005-tilegrid))
$(eval $(call fuzzer,017-clb-precyinit,005-tilegrid))
$(eval $(call fuzzer,018-clb-ram,005-tilegrid))
$(eval $(call fuzzer,019-clb-ndi1mux,005-tilegrid))
$(eval $(call fuzzer,025-bram-config,005-tilegrid))
$(eval $(call fuzzer,026-bram-data,005-tilegrid))
$(eval $(call fuzzer,027-bram36-config,005-tilegrid))
$(eval $(call fuzzer,028-fifo-config,005-tilegrid))
$(eval $(call fuzzer,029-bram-fifo-config,005-tilegrid))
$(eval $(call fuzzer,050-pip-seed,005-tilegrid))
$(eval $(call fuzzer,051-pip-imuxlout-bypalts,050-pip-seed))
$(eval $(call fuzzer,052-pip-clkin,050-pip-seed))
$(eval $(call fuzzer,053-pip-ctrlin,050-pip-seed))
$(eval $(call fuzzer,055-pip-gnd,050-pip-seed))
$(eval $(call fuzzer,056-pip-rem,051-pip-imuxlout-bypalts 052-pip-clkin 053-pip-ctrlin 055-pip-gnd))
$(eval $(call fuzzer,057-pip-bi,056-pip-rem))
ifneq ($(QUICK),Y)
$(eval $(call fuzzer,058-pip-hclk,056-pip-rem))
$(eval $(call fuzzer,060-bram-cascades,005-tilegrid))
$(eval $(call fuzzer,071-ppips,057-pip-bi 058-pip-hclk 060-bram-cascades))
ifneq ($(BITONLY),Y)
$(eval $(call fuzzer,072-ordered_wires,))
$(eval $(call fuzzer,073-get_counts,))
$(eval $(call fuzzer,074-dump_all,005-tilegrid 072-ordered_wires))
endif
endif
$(eval $(call fuzzer,100-dsp-mskpat,005-tilegrid))

quick:
	$(MAKE) QUICK=Y
