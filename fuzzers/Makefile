define fuzzer
all:: $(1)/run.ok
clean::
	$$(MAKE) -C $(1) clean
$(1)/run.ok: $(addsuffix /run.ok,$(2))
	$$(MAKE) -C $(1) run
endef

$(eval $(call fuzzer,001-part-yaml,))
$(eval $(call fuzzer,005-tilegrid,001-part-yaml))
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
$(eval $(call fuzzer,050-intpips,005-tilegrid))
$(eval $(call fuzzer,051-imuxlout,050-intpips))
$(eval $(call fuzzer,052-clkin,050-intpips))
$(eval $(call fuzzer,053-ctrlin,050-intpips))
$(eval $(call fuzzer,054-gfan,050-intpips))
$(eval $(call fuzzer,055-gnd,050-intpips))
$(eval $(call fuzzer,056-rempips,051-imuxlout 052-clkin 053-ctrlin 054-gfan 055-gnd))
$(eval $(call fuzzer,057-bipips,056-rempips))
$(eval $(call fuzzer,058-hclkpips,056-rempips))
$(eval $(call fuzzer,071-ppips,057-bipips 058-hclkpips))
$(eval $(call fuzzer,072-ordered_wires,))
$(eval $(call fuzzer,073-get_counts,))
$(eval $(call fuzzer,074-dump_all,072-ordered_wires))
