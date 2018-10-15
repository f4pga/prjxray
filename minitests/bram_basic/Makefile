all: build/roi_bramd_bit01.diff build/roi_bramd_bits01.diff build/roi_bramds_bit01.diff build/roi_bramis_bit01.diff

clean:
	rm -rf build


# Toggle all bits in a single BRAM data section
build/roi_bramd_bits01.diff: build/roi_bramd_bits0/design.bits build/roi_bramd_bits1/design.bits
	diff build/roi_bramd_bits{0,1}/design.bits >build/roi_bramd_bits01.diff || true

build/roi_bramd_bits0/design.bits:
	PROJECT=roi_bramd_bits0 bash runme.sh

build/roi_bramd_bits1/design.bits:
	PROJECT=roi_bramd_bits1 bash runme.sh


# Toggle one bit in each BRAM data section
build/roi_bramds_bit01.diff: build/roi_bramds_bit0/design.bits build/roi_bramds_bit1/design.bits
	diff build/roi_bramds_bit{0,1}/design.bits >build/roi_bramds_bit01.diff || true

build/roi_bramds_bit0/design.bits:
	PROJECT=roi_bramds_bit0 bash runme.sh

build/roi_bramds_bit1/design.bits:
	PROJECT=roi_bramds_bit1 bash runme.sh


# Toggle one bit in each BRAM config section
build/roi_bramis_bit01.diff: build/roi_bramis_bit0/design.bits build/roi_bramis_bit1/design.bits
	diff build/roi_bramis_bit{0,1}/design.bits >build/roi_bramis_bit01.diff || true

build/roi_bramis_bit0/design.bits:
	PROJECT=roi_bramis_bit0 bash runme.sh

build/roi_bramis_bit1/design.bits:
	PROJECT=roi_bramis_bit1 bash runme.sh

