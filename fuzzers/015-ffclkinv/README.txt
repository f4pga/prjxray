Clock inversion is per slice (as BEL CLKINV)
Vivado GUI is misleading as it often shows it per FF, which is not actually true
0: normal clock
1: invert clock
CLB.SLICE_X0.CLKINV 01_51
CLB.SLICE_X1.CLKINV 00_52

Note: Vivado uses inverted clock macros with "_1" to infer this mux
Ex: FDCE_1 is inverted, FDCE is normal
It is illegal to place both in the same slice
