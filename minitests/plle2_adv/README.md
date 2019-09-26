# PLLE2_ADV minitest

## Description

This test verifies operation of the `PLLE2_ADV` primitive. The PLL is configured to output clocks using the following dividers:

- CLKOUT0: 16/16
- CLKOUT1: 16/32
- CLKOUT2: 16/48
- CLKOUT3: 16/64
- CLKOUT4: 16/80
- CLKOUT5: 16/96

The input clock can be swtched between 100MHz and 50MHz using the `sw[1]` switch. The 50MHz clock is generated using simple divider implemented in logic.

Clocks from the PLL are further divided by 2^21 and then fed to LEDs 0:5. PLL lock indicator is connected to LED 15. The switch `sw[0]` provides reset signal to the PLL.

## Building

To build the project run the following command and the bit file will be generated.
```
make basys3_plle2_adv.bit
```
