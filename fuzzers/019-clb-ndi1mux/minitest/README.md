# CLB_nDI1MUX Minitest

## Purpose
Trying to set SLICEM LUT DI1 inputs
These exist for LUTA, LUTB, and LUTC only
Can either be an external signal, another LUT's data input, or another LUT's carry
Note: mux input pattern is irregular

## Result
The following bits are set for NI but not NMC31:
```
bit 00_00 ADI1MUX.AI
bit 00_20 BDI1MUX.BI
bit 01_43 BDI1MUX.CI
```
Additionally, test with unknown DI mux bits don't appear near NI bits
There is something strange going on

