# FFConfig Fuzzer

Tags for CLB tiles use a dot-separated hierarchy for their tag names. For example the tag `CLBLL_L.SLICEL_X0.ALUT.INIT[00]` documents the bit position of the LSB LUT init bit for the ALUT for the slice with even X coordinate within a `CLBLL_L` tile. (There are 4 LUTs in a slice: ALUT, BLUT, CLUT, and DLUT. And there are two slices in a CLB tile: One with an even X coordinate using the `SLICEL_X0` namespace for tags, and one with an odd X coordinate using the `SLICEL_X1` namespace for tags.)

Also note mapping between FF/latch library elements and CLB FF's:

|  Element | CE | CK | D | SR | Q |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| FDRE | CE | C | D | R | Q |
| FDPE | CE | C | D | PRE | Q |
| FDSE | CE | C | D | S | Q |
| FDCE | CE | C | D | CLR | Q |
| LDPE | GE | G | D | PRE | Q |
| LDCE | GE | G | D | CLR | Q |

And required configuration (as noted below):

|  Element | FFSYNC | LATCH | ZRST |
| ------------- | ------------- | ------------- | ------------- |
| FDPE |  |  |  |
| FDSE | 1 |  |  |
| FDRE | 1 |  | 1 |
| FDCE |  |  | 1 |
| LDCE |  | 1 | 1 |
| LDPE |  | 1 |  |


## CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]*FF.ZINI

Sets GSR FF or latch value

FF
* 0: reset / initialize to 1
* 1: reset / initialize to 0

Latch
* 0: reset / initialize to 0
* 1: reset / initialize to 1

## CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]*FF.ZRST

Set when reset signal should set storage element to 0. Specifically:

 * 0: FDRE, FDCE, and LDCE primitives
 * 1: FDPE, FDSE, and LDPE primitives

## CLBL[LM]_[LR].SLICE[LM]_X[01].[ABCD]LUT.INIT

TBD

## CLBL[LM]_[LR].SLICE[LM]_X[01].FFSYNC

Unlike most bits, shared between all CLB FFs

 * 0: synchronous reset, specifically FDPE, FDCE, LDCE, and LDPE primitives
 * 1: asynchronous reset, specifically FDSE and FDRE primitives

## CLBL[LM]_[LR].SLICE[LM]_X[01].LATCH

Controls latch vs FF behavior for the CLB

 * 0: all storage elements in the CLB are FF's
 * 1: LUT6 storage elements are latches (LDCE or LDPE). LUT5 storage elements cannot be used

## CLBL[LM]_[LR].SLICE[LM]_X[01].CEUSEDMUX

Configure ability to drive clock enable (CE) or always enable clock
* 0: always on (CE=1)
* 1: controlled (CE=mywire)

## CLBL[LM]_[LR].SLICE[LM]_X[01].SRUSEDMUX

Configure ability to reset FF after GSR
* 0: never reset (R=0)
* 1: controlled (R=mywire)

TODO: how used when SR?

## CLBL[LM]_[LR].SLICE[LM]_X[01].CLKINV

Whether to invert the clock going into a slice.

FF:
* 0: normal clock
* 1: invert clock

Latch:
* 0: invert clock
* 1: normal clock

That is, for example, FDSE_1 will have the bit set, but LDCE_1 will have the bit clear.

Note: clock cannot be inverted at individual FF's

