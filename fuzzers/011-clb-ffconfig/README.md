# clb-ffconfig Fuzzer

Documents FF configuration.

Note Vivado GUI is misleading in some cases where it shows configuration per FF, but its actually per SLICE

## Primitive pin map

|  Element | CE | CK | D | SR  | Q |
|----------|----|----|---|-----|---|
| FDRE     | CE | C  | D | R   | Q |
| FDPE     | CE | C  | D | PRE | Q |
| FDSE     | CE | C  | D | S   | Q |
| FDCE     | CE | C  | D | CLR | Q |
| LDPE     | GE | G  | D | PRE | Q |
| LDCE     | GE | G  | D | CLR | Q |


## Primitive bit map

| Prim | FFSYNC | LATCH | ZRST |
|------|--------|-------|------|
|FDPE  |        |       |      |
|FDSE  | X      |       |      |
|FDRE  | X      |       | X    |
|FDCE  |        |       | X    |
|LDCE  |        | X     | X    |
|LDPE  |        | X     |      |


### FFSYNC

Configures whether a storage element is synchronous or asynchronous.

Scope: entire site (not individual FFs)

| FFSYNC | Reset        | Applicable prims          |
|--------|--------------|---------------------------|
|0       | Asynchronous | FDPE, FDCE, LDCE, LDPE    |
|1       | Synchronous  | FDSE, FDRE                |


### LATCH

Configures latch vs FF behavior for the CLB

| LATCH | Description | Primitives |
|-------|-------------|------------|
|0      | All storage elements in the CLB are FF's  | FDPE, FDSE, FDRE, FDCE    |
|1      | LUT6 storage elements are latches (LDCE or LDPE). LUT5 storage elements cannot be used  | LDCE, LDPE    |


### N*FF.ZRST

Configures stored value when reset is asserted

| Prim                  |ZRST|On reset|
|-----------------------|----|-----   |
|FDRE, FDCE, and LDCE   | 0  | 1      |
|FDRE, FDCE, and LDCE   | 1  | 0      |
|FDPE, FDSE, and LDPE   | 0  | 0      |
|FDPE, FDSE, and LDPE   | 1  | 1      |


## N*FF.ZINI

Sets GSR FF or latch value

| LATCH | ZINI | Set to |
|-------|------|--------|
| FF    | 0    | 1      |
| FF    | 1    | 0      |
| LATCH | 0    | 0      |
| LATCH | 1    | 1      |


## CEUSEDMUX

Configures ability to drive clock enable (CE) or always enable clock

| CEUSEDMUX | Description             |
|-----------|-------------------------|
| 0         | always on (CE=1)        |
| 1         | controlled (CE=mywire)  |


## SRUSEDMUX

Configures ability to reset FF after GSR

| SRUSEDMUX | Description           |
|-----------|-----------------------|
| 0         | never reset (R=0)     |
| 1         | controlled (R=mywire) |

TODO: how used when SR?

## CLKINV

Configures whether to invert the clock going into a slice.

Scope: entire site (not individual FFs)

| LATCH | CLKINV | Description    |
|-------|--------|----------------|
| FF    | 0      | normal clock   |
| FF    | 1      | invert clock   |
| LATCH | 0      | invert clock   |
| LATCH | 1      | normal clock   |

