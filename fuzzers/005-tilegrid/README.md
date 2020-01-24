# Tilegrid Fuzzer

This fuzzer creates the tilegrid.json bitstream database.
This database contains segment definitions including base frame address and frame offsets.

## Example workflow for CLB
generate.tcl LOCs one LUT per segment column towards generating frame base addresses.

A reference bitstream is generated and then:
- a series of bitstreams are generated each with one LUT bit toggled; then
- these are compared to find a toggled bit in the CLB segment column; then
- the resulting address is truncated to get the base frame address.

Finally, generate.py calculates the segment word offsets based on known segment column structure

## Environment variables

### XRAY_ROI
This environment variable must be set with a valid ROI.
See database for example values

### XRAY_EXCLUDE_ROI_TILEGRID
This environment variable must be set in case the part selected does not allow some tiles to be
locked.

Error example (when using the artix 200T part):
`ERROR: [Place 30-25] Component carry4_SLICE_X82Y249 has been locked to a prohibited site SLICE_X82Y249.`

To avoid this error, the `XRAY_EXCLUDE_ROI_TILEGRID` defines an ROI that is not taken into account
when building the tilegrid, therefore excluding the problematic un-lockable sites.

As the resulting output file, `tilegrid.json`, is going to be checked against the one produced in
the `074-dump_all` fuzzer, also the latter one needs to produce a reduced tilegrid, with the excluded
tiles specified with the environment variable.


### XRAY_ROI_FRAMES
This can be set to a specific value to speed up processing and reduce disk space
If you don't know where your ROI is, just set to to include all values (0x00000000:0xfffffff)

### XRAY_ROI_GRID_*
Optionally, use these as a small performance optimization:
- XRAY_ROI_GRID_X1
- XRAY_ROI_GRID_X2
- XRAY_ROI_GRID_Y1
- XRAY_ROI_GRID_Y2

These should, if unused, be set to -1, with this caveat:

WARNING: CLB test generates this based on CLBs but implicitly includes INT

Therefore, if you don't set an explicit XRAY_ROI_GRID_* it may fail
if you don't have a CLB*_L at left and a CLB*_R at right.
