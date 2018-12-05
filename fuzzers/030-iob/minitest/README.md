# PULLTYPE

PULLTYPE    28  29  30
NONE                X
KEEPER      X       X
PULLDOWN
PULLUP          X   X


# DRIVE

DRIVE       A00 A02 A08 A10 B09 B01
0           FIXME
4           X   X           X
8               X   X           X
12          X   X               X
16          X           X   X
24          FIXME


# IOSTANDARD

Effects bits, TBD exactly how
Sample output:

diff LVCMOS33.bits LVTTL.bits
< bit_00020026_006_00
> bit_00020026_006_08

diff LVCMOS33.bits PCI33_3.bits
< bit_00020026_006_02
< bit_00020026_006_18
< bit_00020026_006_22
> bit_00020026_006_10
> bit_00020026_006_16
> bit_00020026_006_20
> bit_00020027_006_11
> bit_00020027_006_15

