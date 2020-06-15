# Minitests for IDELAY

## 1. basys3_idelay_var

A design for Basys3 board.

### Description

This test generates a 50MHz square wave on an output pin which is then fed back to the FPGA IDELAY bel through another input pin. The delayed signal is then routed to yet another output pin which allows it to be compared with the input signal using an oscilloscope. The IDELAY is calibrated using 100MHz clock hence delays from 0 to 5ns can be achieved.

The switch `SW0` acts as reset. The switch `SW1` allows to change the delay value. One toggle of that switch increases the delay counter by one.

The `LED0` blinks continuously. The `LED1` indicates that the calibration of IDELAY has been completed (the `RDY` signal from IDELAYCTRL bel). Leds `LED11` through `LED15` indicate current delay setting (the `CNTVALUEOUT` of IDELAY bel).

### Physical loopback

Consider the `JXADC` connector on the Basys3 board as seen when looking at the board edge:
```
 -- -- -- -- -- --
| 6| 5| 4| 3| 2| 1|
 -- -- -- -- -- --
|12|11|10| 9| 8| 7|
 -- -- -- -- -- --
```

 - Pin1 - Signal output. Connect to CH1 of the oscilloscope.
 - Pin2 - Delayed signal output. Connect to CH2 of the oscilloscope.
 - Pin7 - Delay signal input, connect to Pin8.
 - Pin8 - Signal output. Connect to Pin7.

**The oscilloscope must have bandwidth of at least 100MHz.**

## 2. basys3_idelay_const

This design generates 32 independently shifted 50MHz square waves using constant delay IDELAY blocks. Delays between individual signals can be measured using an oscilloscope. Due to the fact that each delay step is about 100-150ps and the FPGA fabric + IOBs also introduce their own delays, actual delay values may be hard to measure.

## 3. basys3_idelay_histogram

This design transmitts a pseudo-random data stream throught one output pin and then receives it through another one with the use of IDELAY. A physical loopback is required. The received data is compared with the transmitted one. Receive errors are counted separately for each one of 32 possible delay settings of the IDELAY bel. Values of 32 error counters are periodically pinted using the UART as an ASCII string.

There is a control state machine which performs the following sequence once per ~0.5s (adjustable).

 1. Set delay of the IDELAY bel.
 2. Wait for it to stabilize (a few clock cycles)
 3. Compare received and transmitted data and count errors. Do it for some period of time (adjustable).
 4. Repeat steps 1-4 for all 32 delay steps
 5. Output error counters through the UART
 6. Wait

The physical loopback has to be connected between `JXADC.7` and `JXADC.8` pins.

Example UART output:

```
...
0027F_000277_00026D_00025C_00027C_00028B_000265_000275_000265_000271_000275_000255_00027A_000280_00027B_000265_00027B_00027A_00025D_000263_000256_00026F_000293_000268_000286_000260_000269_000275_000266_00026D_000273_000272
00281_000271_000273_00026B_000273_000271_00025F_000279_00027D_000283_000266_000279_000274_00025D_000261_000260_00026F_000287_00026E_000289_000261_000267_00027A_00026C_00026D_000270_00026C_00027C_000251_000266_00027A_000283
00271_000255_00027D_000283_000283_00025B_00027E_000271_000263_000259_000262_000270_00027E_00026F_00027D_000267_00026C_00026E_00026E_00027B_00026F_00026D_000279_000250_00026E_00027E_000282_000267_000270_000262_000237_000284
...
```

There are 32 hex numbers separated by "_". Each one correspond to one error counter.
