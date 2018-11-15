# Intended for CIT quick checks
# Full run ("Makefile"): 10 hours
# quick.mk (FUZZONLY=N): 30 min
# quick.mk (FUZZONLY=Y): 6 min

FUZZONLY=N

define fuzzer
all:: $(1)/run.ok
clean::
	$$(MAKE) -C $(1) clean
$(1)/run.ok: $(addsuffix /run.ok,$(2))
	$$(MAKE) -C $(1) run
endef

ifneq ($(FUZZONLY),Y)
$(eval $(call fuzzer,001-part-yaml,))
$(eval $(call fuzzer,005-tilegrid,001-part-yaml))
endif

$(eval $(call fuzzer,010-lutinit,005-tilegrid))
$(eval $(call fuzzer,011-ffconfig,005-tilegrid))
$(eval $(call fuzzer,012-clbn5ffmux,005-tilegrid))
$(eval $(call fuzzer,013-clbncy0,005-tilegrid))
$(eval $(call fuzzer,014-ffsrcemux,005-tilegrid))
$(eval $(call fuzzer,015-clbnffmux,005-tilegrid))
$(eval $(call fuzzer,016-clbnoutmux,005-tilegrid))
$(eval $(call fuzzer,017-clbprecyinit,005-tilegrid))
$(eval $(call fuzzer,018-clbram,005-tilegrid))
$(eval $(call fuzzer,019-ndi1mux,005-tilegrid))
$(eval $(call fuzzer,025-bram-config,005-tilegrid))
$(eval $(call fuzzer,026-bram-data,005-tilegrid))
