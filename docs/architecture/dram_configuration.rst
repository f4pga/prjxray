Distributed RAMs (DRAM / SLICEM)
================================

The SLICEM site can turn the 4 LUT6s into distributed RAMs.  There are a number of modes, each element is either a 64x1 or a 32x2 distributed RAM (DRAM).  The individual elements can be combined into either a 128x1 or 256x1 DRAM.

Functions
---------

Modes
~~~~~
Some modes can be enabled at the single LUT level.  The following modes are:

- 32x2 Single port (32x2S)
- 32x2 Dual port (32x2D)
- 64x1 Single port (64x1S)
- 64x1 Dual port (64x1D)

Some modes are SLICEM wide:

- 128x1 Single port (128x1S)
- 128x1 Dual port (128x1D)
- 256x1

Ports
~~~~~

Each LUT element when operating in RAM mode is a DPRAM64.

+------------+------------+-----------+--------------+
| Port name  | Direction  | Width     | Description  |
+============+============+===========+==============+
| WA         | IN         | 8         | Write address|
+------------+------------+-----------+--------------+
| A          | IN         | 6         | Read address |
+------------+------------+-----------+--------------+
| DI         | IN         | 2         | Data input   |
+------------+------------+-----------+--------------+
| WE         | IN         | 1         | Write enable |
+------------+------------+-----------+--------------+
| CLK        | IN         | 1         | Clock        |
+------------+------------+-----------+--------------+
| O6         | OUT        | 1         | Data output 1|
+------------+------------+-----------+--------------+
| O5         | OUT        | 1         | Data output 2|
+------------+------------+-----------+--------------+

Configuration
-------------

The configuration for the DRAM is found in the following segbits:

- ALUT.RAM
- ALUT.SMALL
- ADI1MUX.AI
- BLUT.RAM
- BLUT.SMALL
- BDI1MUX.BI
- CLUT.RAM
- CLUT.SMALL
- CDI1MUX.CI
- DLUT.RAM
- DLUT.SMALL
- WA7USED
- WA8USED

In order to use DRAM in a SLICEM, the DLUT in the SLICEM must be a RAM (e.g. DLUT.RAM).
In addition the DLUT can never be a dual port RAM because the write address lines for the DLUT are also the read address lines.

Segbits for modes
~~~~~~~~~~~~~~~~~

The following table shows the features required for each mode type for each LUT.

+------+------------+------------+------------+----------+
| LUTs | 32x2S      | 32x2D      | 64x1S      | 64x1D    |
+------+------------+------------+------------+----------+
| D    | DLUT.RAM   | N/A        | DLUT.RAM   | N/A      |
|      |            |            |            |          |
|      | DLUT.SMALL |            |            |          |
+------+------------+------------+------------+----------+
| C    | CLUT.RAM   | CLUT.RAM   | CLUT.RAM   | CLUT.RAM |
|      |            |            |            |          |
|      | CLUT.SMALL | CLUT.SMALL | CDI1MUX.CI |          |
|      |            |            |            |          |
|      | CDI1MUX.CI |            |            |          |
+------+------------+------------+------------+----------+
| B    | BLUT.RAM   | BLUT.RAM   | BLUT.RAM   | BLUT.RAM |
|      |            |            |            |          |
|      | BLUT.SMALL | BLUT.SMALL | BDI1MUX.CI |          |
|      |            |            |            |          |
|      | BDI1MUX.CI |            |            |          |
+------+------------+------------+------------+----------+
| A    | ALUT.RAM   | ALUT.RAM   | ALUT.RAM   | ALUT.RAM |
|      |            |            |            |          |
|      | ALUT.SMALL | ALUT.SMALL | ADI1MUX.CI |          |
|      |            |            |            |          |
|      | ADI1MUX.CI |            |            |          |
+------+------------+------------+------------+----------+

Ports for modes
~~~~~~~~~~~~~~~

In each mode, how the ports are used vary.  The following table show the relationship between the LUT mode and ports.

+------+-------------------------------------+----------------------------+----------------------------------------+-------------------------------+
| LUTs | 32x2S                               | 32x2D                      | 64x1S                                  | 64x1D                         |
+------+-------------------------------------+----------------------------+----------------------------------------+-------------------------------+
| D    | WA[4:0] = A[4:0] = {D5,D4,D3,D2,D1} | N/A                        | WA[5:0] = A[5:0] = {D6,D5,D4,D3,D2,D1} | N/A                           |
|      |                                     |                            |                                        |                               |
|      | DI[1:0] = {DX, DI}                  |                            | DI[0] = DI                             |                               |
+------+-------------------------------------+----------------------------+----------------------------------------+-------------------------------+
| C    | WA[4:0] = A[4:0] = {C5,C4,C3,C2,C1} | WA[4:0] = {D5,D4,D3,D2,D1} | WA[5:0] = A[5:0] = {C6,C5,C4,C3,C2,C1} | WA[5:0] = {D6,D5,D4,D3,D2,D1} |
|      |                                     |                            |                                        |                               |
|      | DI[1:0] = {CX, CI}                  | A[4:0] = {C5,C4,C3,C2,C1}  |                                        | A[5:0] = {C6,C5,C4,C3,C2,C1}  |
|      |                                     |                            |                                        |                               |
|      |                                     | DI[1:0] = {CX,DI}          | DI[0] = CI                             | DI[0] = DI                    |
+------+-------------------------------------+----------------------------+----------------------------------------+-------------------------------+
| B    | WA[4:0] = A[4:0] = {B5,B4,B3,B2,B1} | WA[4:0] = {D5,D4,D3,D2,D1} | WA[5:0] = A[5:0] = {B6,B5,B4,B3,B2,B1} | WA[5:0] = {D6,D5,D4,D3,D2,D1} |
|      |                                     |                            |                                        |                               |
|      |                                     | A[4:0] = {B5,B4,B3,B2,B1}  |                                        | A[5:0] = {B6,B5,B4,B3,B2,B1}  |
|      | DI[1:0] = {BX, BI}                  |                            | DI[0] = BI                             |                               |
|      |                                     | DI[1:0] = {BX,DI}          |                                        | DI[0] = DI                    |
+------+-------------------------------------+----------------------------+----------------------------------------+-------------------------------+
| A    | WA[4:0] = A[4:0] = {A5,A4,A3,A2,A1} | WA[4:0] = {D5,D4,D3,D2,D1} | WA[5:0] = A[5:0] = {A6,A5,A4,A3,A2,A1} | WA[5:0] = {D6,D5,D4,D3,D2,D1} |
|      |                                     |                            |                                        |                               |
|      | DI[1:0] = {AX, AI}                  | A[4:0] = {A5,A4,A3,A2,A1}  | DI[0] = AI                             | A[5:0] = {A6,A5,A4,A3,A2,A1}  |
|      |                                     |                            |                                        |                               |
|      |                                     | DI[1:0] = {AX,BLUT.DI[0]}  |                                        | DI[0] = BLUT.DI[0]            |
+------+-------------------------------------+----------------------------+----------------------------------------+-------------------------------+


Techlib macros
~~~~~~~~~~~~~~

The tech library exposes the following aggregate modes, which are accomplished with the following combinations.

+----------+--------------+--------------+--------------+--------------+
| Macro    | Option 1     | Option 2     | Option 3     | Option 4     |
+----------+--------------+--------------+--------------+--------------+
| RAM32M   | DLUT = 32x2S |              |              |              |
|          |              |              |              |              |
|          | CLUT = 32x2D |              |              |              |
|          |              |              |              |              |
|          | BLUT = 32x2D |              |              |              |
|          |              |              |              |              |
|          | ALUT = 32x2D |              |              |              |
+----------+--------------+--------------+--------------+--------------+
| RAM32X1D | DLUT = 32x2S | BLUT = 32x2S |              |              |
|          |              |              |              |              |
|          | CLUT = 32x2D | ALUT = 32x2D |              |              |
+----------+--------------+--------------+--------------+--------------+
| RAM32X1S | DLUT = 32x1S | CLUT = 32x1S | BLUT = 32x1S | ALUT = 32x1S |
+----------+--------------+--------------+--------------+--------------+
| RAM32X2S | DLUT = 32x2S | BLUT = 32x2S |              |              |
|          |              |              |              |              |
|          | CLUT = 32x2D | ALUT = 32x2D |              |              |
+----------+--------------+--------------+--------------+--------------+
| RAM64M   | DLUT = 64x1S |              |              |              |
|          |              |              |              |              |
|          | CLUT = 64x1D |              |              |              |
|          |              |              |              |              |
|          | BLUT = 64x1D |              |              |              |
|          |              |              |              |              |
|          | ALUT = 64x1D |              |              |              |
+----------+--------------+--------------+--------------+--------------+
| RAM64X1D | DLUT = 64x1S | BLUT = 64x1S |              |              |
|          |              |              |              |              |
|          | CLUT = 64x1D | ALUT = 64x1D |              |              |
+----------+--------------+--------------+--------------+--------------+
| RAM64X1S | DLUT = 64x1S | CLUT = 64x1S | BLUT = 64x1S | ALUT = 64x1S |
+----------+--------------+--------------+--------------+--------------+

