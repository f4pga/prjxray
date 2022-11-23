# IOB18 Fuzzer

This fuzzer solves the bits related to the IO pads in the
high performance banks, which are present in most of the
Kintex and Virtex devices (a notable exception are K420T and K480T)
using bank numbers of 30 and above.

These banks have a maximum voltage of 1.8V which is the reason
why many of the BEL names end in 18 (as opposed to 33 for the
high range banks, which run on a maximum voltage of 3.3V).

Currently the focus is on supporting the most used IO standards;
On most boards, the high performance banks are connected to DDR3
memory and this mandates the support of single ended and differential
SSTL15. 
Of course, all the LVCMOS variants and LVDS are a must have too.

Currently unsupported are digitally controlled impedance
(usually indicated by the regular IO standard names with a
_DCI and _T_DCI suffix).
