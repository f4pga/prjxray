# Minitests for IDELAY

## 1. basys3_idelay_ext

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