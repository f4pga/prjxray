# PULLTYPE

PULLTYPE    38_98   39_97  39_97
NONE                  X
KEEPER       X        X
PULLDOWN
PULLUP       X        	     X


# DRIVE

Drive strength depends on current IOSTANDARD, e.g.

LVCMOS18
DRIVE     38_64    38_66    38_72    38_74    39_65    39_73
4           X        X                                   X
8                    X        X                 X
12                   X        X                 X
16          X        X                          X
24                            X        X        X

LVCMOS25
DRIVE     38_64    38_66    38_72    38_74    39_65    39_73
4           X        X                                   X
8                             X
12
16                                     X        X        X

LVCMOS33
DRIVE     38_64    38_66    38_72    38_74    39_65    39_73
4           X        X                                   X
8                    X        X                 X
12          X        X                          X
16          X                          X                 X

The minitest contains a csv target which generates a csv with differences across all LVCMOS and LVTTL standards for all supported DRIVE strengths and both slew rates.

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

