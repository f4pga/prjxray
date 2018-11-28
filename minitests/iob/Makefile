all:  build/env build/roi_roi_io.diff

clean:
	rm -rf build

# hard coded LOCs in .v
build/env:
	test "$(XRAY_PART)" = "xc7a50tfgg484-1"

build/roi_roi_io.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_io.diff PRJL=roi_io_a PRJR=roi_io_b


