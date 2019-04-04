# Generic fuzzer for INT PIPs

Run this fuzzer a few times until it stops adding new PIPs to the
database.

Sample runs:
* 78fa4bd5
  * jenkins 3, success
  * intpips: 1 iter, N=200, -m 5 -M 15
  * intpips todo final: N/A
  * intpips segbits_int_l.db lines: 3374
  * rempips todo initial: 279
  * rempips todo final (32): 9
* 20e09ca7
  * jenkins 21, rempips failure
  * intpips: 6 iters, N=48, -m 15 -M 45
  * intpips segbits_int_l.db lines: 3364
  * rempips todo initial: 294
  * rempips todo final (51): 294
* 1182359f
  * jenkins 23, intpips failure
  * inpips: 12 iters, N=48, -m 15 -M 45
  * intpips todo final: 495
  * inpips segbits_int_l.db lines: 5167
  * rempips todo: N/A


### const0

These show up in large numbers after a full solve.
This means that it either has trouble solving these or simply cannot.
Counts from sample run

Includes:
* INT.BYP_ALT\*.LOGIC_OUTS\* (24)
  * Ex: INT.BYP_ALT2.LOGIC_OUTS14
* INT.[NESW]\*.LOGIC_OUTS\* (576)
  * Ex: INT.EE4BEG2.LOGIC_OUTS2
  * Ex: INT.EL1BEG_N3.LOGIC_OUTS0
  * Ex: INT.WR1BEG3.LOGIC_OUTS2
* INT.IMUX*.* (1151)
  * Ex: INT.IMUX0.NL1END0
  * Ex: INT.IMUX0.FAN_BOUNCE7
  * Ex: INT.IMUX14.LOGIC_OUTS7


### GFAN

Includes:
* Easily solves: INT.IMUX_L*.GFAN*
* Can solve: INT.BYP_ALT*.GFAN*
* Cannot solve: INT.IMUX*.GFAN* (solves as "<m1 0> <const0>")

### IMUX

* Okay: BYP_ALT*.VCC_WIRE
* Cannot solve: INT.IMUX[0-9]+.VCC_WIRE
* Cannot solve: INT.IMUX_L[0-9]+.VCC_WIRE

See https://github.com/SymbiFlow/prjxray/issues/383

