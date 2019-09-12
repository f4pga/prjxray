# ISERDES minitest for SDR and DDR

## Description

This test allows to verify that ISEDRES is working on hardware. Tested modes are:
- NETWORKING / SDR
- NETWORKING / DDR

No chaining of two ISERDES bels.

The design serializes data using logic for all tested ISERDES modes. The data is presented onto selected pins. The same pins are used to receive the data which is then fed to ISERDES cells. No physical loopback is required. The clock is routed internally.

The received data is compared against transmitted internally. Errors are
indicated using LEDs. The comparator module automatically invokes the bitslip
feature of ISERDES (by brutaly testing all possible combinations).

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

## Building

To build the project run the following command and the bit file will be generated.
```
make basys3_iserdes_sdr_ddr.bit
```
