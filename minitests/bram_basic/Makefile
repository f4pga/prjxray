all:  build/roi_bramd_bit01.diff build/roi_bramd_bits01.diff build/roi_bramds_bit01.diff build/roi_bramis_bit01.diff

clean:
	rm -rf build

# Toggle one bit to locate where first BRAM data is
build/roi_bramd_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramd_bit01.diff PRJL=roi_bramd_bit0 PRJR=roi_bramd_bit1

# Toggle all bits in a single BRAM data section
build/roi_bramd_bits01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramd_bits01.diff PRJL=roi_bramd_bits0 PRJR=roi_bramd_bits1

# Toggle one bit in each BRAM data section
build/roi_bramds_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramds_bit01.diff PRJL=roi_bramds_bit0 PRJR=roi_bramds_bit1

# Toggle one bit in each BRAM config section
build/roi_bramis_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramis_bit01.diff PRJL=roi_bramis_bit0 PRJR=roi_bramis_bit1

