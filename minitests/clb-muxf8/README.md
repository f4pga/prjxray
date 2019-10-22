# CLB_MUXF8 Minitest

## Purpose
This tests an issue related to Vivado 2017.2 vs 2017.3 changing MUXF8 behavior
The general issue is the LUT6_2 cannot be used with a MUXF8 (even if O5 is unused)

## General notes:
- 2017.2: LUT6_2 works with MUXF8
- 2017.3: LUT6_2 does not work with MUXF8
- All: LUT6 works with MUXF8
- All: MUXF8 (even with MUXF7) can be instantiated unconnected
- 2017.4 seems to behave like 2017.3

