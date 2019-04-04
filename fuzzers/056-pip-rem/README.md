# Fuzzer for the remaining INT PIPs

Run this fuzzer a few times until it produces an empty todo.txt file (`make run` will run this loop).

This fuzzer occationally fails (depending on some random variables). Just restart it if you encounter
this issue. The script behind `make run` automatically handles errors by re-starting a run if an error
occurs.

### Solvability

Known issues:
* INT.CTRL0: goes into CLB's SR. This cannot be routed through

Jenkins build 3 (78fa4bd5, success) for example solved the following types:
 * INT_L.EE4BEG0.LH12
 * INT_L.FAN_ALT1.GFAN1
 * INT_L.FAN_ALT4.BYP_BOUNCE_N3_3
 * INT_L.LH0.EE4END3
 * INT_L.LH0.LV_L9
 * INT_L.LH0.SS6END3
 * INT_L.LVB_L12.WW4END3
 * INT_L.SW6BEG0.LV_L0

