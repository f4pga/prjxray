# ISERDES minitest for SDR and DDR

This test allows to verify that ISEDRES is working on hardware. Tested modes are:
- NETWORKING / SDR
- NETWORKING / DDR

No chaining of two ISERDES bels.

The design uses JA, JB and JC connectors of the Basys 3 boards to output
serialized data and then receive it using ISERDESes. There is a need to
provide physical loopbacks of pins of those connectors. The clock is being
routed internally.

The received data is compared against transmitted internally. Errors are
indicated using LEDs. The comparator module automatically invokes the bitslip
feature of ISERDES (by brutaly testing all possible combinations).

The pinout (out, in):

- JB.1,  JB.7  - SDR, WIDTH=2
- JB.2,  JB.8  - SDR, WIDTH=3
- JB.3,  JB.9  - SDR, WIDTH=4
- JB.4,  JB.10 - SDR, WIDTH=5
- JC.1,  JC.7  - SDR, WIDTH=6
- JC.2,  JC.8  - SDR, WIDTH=7
- JC.3,  JC.9  - SDR, WIDTH=8
- JC.4,  JC.10 - DDR, WIDTH=4
- JA.4,  JA.10 - DDR, WIDTH=6
- JA.3,  JA.9  - DDR, WIDTH=8
- JA.2         - Serialized data clock
- JA.1         - Serialized data clock x2

LEDs indicate whether data is being received corectly. When a LED is lit then
there is correct reception:

- LED0  - SDR, WIDTH=2
- LED1  - SDR, WIDTH=3
- LED2  - SDR, WIDTH=4
- LED3  - SDR, WIDTH=5
- LED4  - SDR, WIDTH=6
- LED5  - SDR, WIDTH=7
- LED6  - SDR, WIDTH=8
- LED7  - DDR, WIDTH=4
- LED8  - DDR, WIDTH=5
- LED9  - DDR, WIDTH=6
- LED10 - Blinking

The switch SW0 is used as reset.

To build the project run the following command and the bit file will be generated.
```
make basys3_top.bit
```
