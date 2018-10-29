all:  build/env build/roi_bramd_bit01.diff build/roi_bramd_bits01.diff build/roi_bramds_bit01.diff build/roi_bramis_bit01.diff

clean:
	rm -rf build

# hard coded LOCs in .v
build/env:
	test "$(XRAY_PART)" = "xc7a50tfgg484-1"

# Toggle one bit to locate where first BRAM data is
build/roi_bramd_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramd_bit01.diff PRJL=roi_bramd_bit0 PRJR=roi_bramd_bit1

build/roi_bramd2_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramd2_bit01.diff PRJL=roi_bramd_bit0 PRJR=roi_bramd2_bit1

# Toggle all bits in a single BRAM data section
build/roi_bramd_bits01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramd_bits01.diff PRJL=roi_bramd_bits0 PRJR=roi_bramd_bits1

# Toggle one bit in each BRAM data section
build/roi_bramds_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramds_bit01.diff PRJL=roi_bramds_bit0 PRJR=roi_bramds_bit1

# Toggle one bit in BRAM config section
build/roi_brami_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_brami_bit01.diff PRJL=roi_brami_bit0 PRJR=roi_brami_bit1

# Toggle one bit in each BRAM18 config section
# together they match the 2 BRAM36 bits above
build/roi_bram18iy0_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18iy0_bit01.diff PRJL=roi_bram18i_bit0 PRJR=roi_bram18iy0_bit1
build/roi_bram18iy1_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18iy1_bit01.diff PRJL=roi_bram18i_bit0 PRJR=roi_bram18iy1_bit1

# Toggle one bit in each BRAM config section
build/roi_bramis_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramis_bit01.diff PRJL=roi_bramis_bit0 PRJR=roi_bramis_bit1

build/roi_bram18_width.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18_width.diff PRJL=roi_bram18_width_a PRJR=roi_bram18_width_b

