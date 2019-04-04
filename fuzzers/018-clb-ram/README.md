# clb-ram Fuzzer

| Primitive  | RAM | SMALL | SRL |
|------------|-----|-------|-----|
| LUT6       |     |       |     |
| SRL16E     |     | X     | X   |
| SRLC32E    |     |       | X   |
| RAM32X1S   | X   | X     |     |
| RAM64X1S   | X   |       |     |
| RAM32M     | X   | X     |     |
| RAM32X1D   | X   | X     |     |
| RAM64M     | X   |       |     |
| RAM64X1D   | X   |       |     |
| RAM128X1D  | X   |       |     |
| RAM256X1S  | X   |       |     |
| RAM128X1S  | X   |       |     |


## NLUT.RAM

Set to make a RAM* family primitive, otherwise is a SRL or LUT function generator.


## NLUT.SMALL

Seems to be set on smaller primitives.


## NLUT.SRL

Whether to make a shift register LUT (SRL). Set when using SRL16E or SRLC32E


## WA7USED

Set to 1 to propagate CLB's CX input to WA7


## WA8USED

Set to 1 to propagate CLB's BX input to WA8


## WEMUX.CE

| WEMUX.CE  | CLB RAM write enable |
|-----------|----------------------|
| 0         | CLB WE input         |
| 1         | CLB CE input         |

