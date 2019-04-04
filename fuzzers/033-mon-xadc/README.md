# XADC Fuzzer

As of this writing, this fuzzer is not in the ROI
To use it, you must run tilegrid first with these options (artix7):

export XRAY_ROI_GRID_Y2=103
export XRAY_ROI="SLICE_X0Y100:SLICE_X35Y149 RAMB18_X0Y40:RAMB18_X0Y59 RAMB36_X0Y20:RAMB36_X0Y29 DSP48_X0Y40:DSP48_X0Y59 IOB_X0Y100:IOB_X0Y149 XADC_X0Y0:XADC_X0Y0"
005-tilegrid$ make monitor/build/segbits_tilegrid.tdb
005-tilegrid$ make

Then run this fuzzer

