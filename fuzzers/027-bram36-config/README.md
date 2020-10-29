RAMB36 features
===============

This fuzzer emits features that only are used in the RAMB36E1 cell.  There are
3 categories:

 - ECC
 - RAM extension
 - Odd address modes

Odd address modes
-----------------

Most RAMB36E1 address widths are expressed by configuring the underlying
RAMB18E1 to handle half of the data.  So `RAMB36.READ_WIDTH = 4` is
expressed as `RAM18_Y0.READ_WIDTH = 2` and `RAM18_Y1.READ_WIDTH = 2`.  However
two address widths (1 and 9) are odd (e.g. not divisible by 2).  In these
cases, a RAMB36E1 specific feature is used.  So `RAMB36.READ_WIDTH = 9` is
expressed as:

 - `RAMB18_Y0.READ_WIDTH_4`
 - `RAMB18_Y1.READ_WIDTH_4`
 - `RAMB36.BRAM36_READ_WIDTH_1`

and `RAMB36.READ_WIDTH = 1` is expressed as:

 - `RAMB18_Y0.READ_WIDTH_1`
 - `RAMB18_Y1.READ_WIDTH_1`
 - `RAMB36.BRAM36_READ_WIDTH_1`
