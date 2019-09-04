# Minitests for ISERDES+IDELAY

## 1. basys3_iserdes_idelay_histogram

This design transmitts a pseudo-random data stream throught one output pin and then receives it through another one with the use of IDELAY and ISERDES. A physical loopback is required. The received data is serialized again (internally) and the received bitstream compared with the transmitted one. This is agnostic to ISERDES configuration. Receive errors are counted separately for each one of 32 possible delay settings of the IDELAY bel. Values of 32 error counters are periodically pinted using the UART as an ASCII string.

There is a control state machine which performs the following sequence once per ~0.5s (adjustable).

 1. Set delay of the IDELAY bel.
 2. Wait for it to stabilize (a few clock cycles)
 3. Compare received and transmitted data and count errors. Do it for some period of time (adjustable).
 4. Repeat steps 1-4 for all 32 delay steps
 5. Output error counters through the UART
 6. Wait

The physical loopback has to be connected between `JXADC.7` and `JXADC.8` pins.

Consider the `JXADC` connector on the Basys3 board as seen when looking at the board edge:
```
 -- -- -- -- -- --
| 6| 5| 4| 3| 2| 1|
 -- -- -- -- -- --
|12|11|10| 9| 8| 7|
 -- -- -- -- -- --
```

 - Pin1 - Received signal output, through IDELAY and ISERDES.O (for reference)
 - Pin2 - Transmitted signal output (for reference).
 - Pin3 - Serialized data clock that the ISERDES operates on (for reference)
 - Pin7 - Physical loopback input, connect to Pin8
 - Pin8 - Physical loopback output, connect to Pin7

**Important: Make the connection between Pin7 and Pin8 no longer than ~10cm (~4inch).** You can use cables of different length to see how it affects the signal delay.

Example UART output:

```
...
0027F_000277_00026D_00025C_00027C_00028B_000265_000275_000265_000271_000275_000255_00027A_000280_00027B_000265_00027B_00027A_00025D_000263_000256_00026F_000293_000268_000286_000260_000269_000275_000266_00026D_000273_000272
00281_000271_000273_00026B_000273_000271_00025F_000279_00027D_000283_000266_000279_000274_00025D_000261_000260_00026F_000287_00026E_000289_000261_000267_00027A_00026C_00026D_000270_00026C_00027C_000251_000266_00027A_000283
00271_000255_00027D_000283_000283_00025B_00027E_000271_000263_000259_000262_000270_00027E_00026F_00027D_000267_00026C_00026E_00026E_00027B_00026F_00026D_000279_000250_00026E_00027E_000282_000267_000270_000262_000237_000284
...
```

There are 32 hex numbers separated by "_". Each one correspond to one error counter.

An utility script `iserdes_idelay_histogram_receiver.p` can be found in the `utils` subdirectory. It reads and parses data received through UART and prints counter values in decimal.