# ROI_HARNESS Minitest

## Purpose

Creates an harness bitstream which maps peripherals into a region of interest
which can be reconfigured.

The currently supported boards are;

 * Artix 7 boards;
  - [Basys 3](https://github.com/SymbiFlow/prjxray-db/tree/master/artix7/harness#basys-3)
  - [Arty A7-35T](https://github.com/SymbiFlow/prjxray-db/tree/master/artix7/harness#arty-a7-35t)

 * Zynq boards;
  - [Zybo Z7-10](https://github.com/SymbiFlow/prjxray-db/tree/master/zynq7/harness#zybo-z7-10)

The following configurations are supported;

 * SWBUT - Harness which maps a board's switches, buttons and LEDs into the
   region of interest (plus clock).


 * PMOD - Harness which maps a board's PMOD connectors into the region of
   interest (plus a clock).

 * UART - Harness which maps a board's UART


"ARTY-A7-SWBUT"
        # 4 switches then 4 buttons
        A8 C11 C10 A10  D9 C9 B9 B8
        # 4 LEDs then 4 RGB LEDs (green only)
        H5 J5 T9 T10  F6 J4 J2 H6

        # clock
	E3

"ARTY-A7-PMOD"
        # CLK on Pmod JA
	G13 B11 A11 D12  D13 B18 A18 K16
        # DIN on Pmod JB
        E15 E16 D15 C15  J17 J18 K15 J15
        # DOUT on Pmod JC
	U12 V12 V10 V11  U14 V14 T13 U13

"ARTY-A7-UART"
        # RST button and UART_RX
        C2 A9
        # LD7 and UART_TX
        T10 D10
        # 100 MHz CLK onboard
        E3

"BASYS3-SWBUT"
        # Slide switch pins
        V17 V16 W16 W17 W15 V15 W14 W13 V2 T3 T2 R3 W2 U1 T1 R2
	# LEDs pins
        U16 E19 U19 V19 W18 U15 U14 V14 V13 V3 W3 U3 P3 N3 P1 L1

        # UART
        B18 # ins
        A18 # outs

        # 100 MHz CLK onboard
        W5

"ZYBOZ7-SWBUT"
        # J15 - UART_RX - JE3
        # G15 - SW0
        # K18 - BTN0
        # K19 - BTN1
        J15  G15  K18 K19

        # H15 - UART_TX - JE4
        # E17 - ETH PHY reset (active low, keep high for 125 MHz clock)
        # M14 - LD0
        # G14 - LD2
        # M15 - LD1
        # D18 - LD3

        # 125 MHz CLK onboard
        K17

## Quickstart

```
source settings/artix7.sh
cd minitests/roi_harness
source arty-swbut.sh
make clean
make copy
```

## How it works

Basic idea:
- LOC LUTs in the ROI to terminate input and output routing
- Let Vivado LOC the rest of the logic
- Manually route signals in and out of the ROI enough to avoid routing loops into the ROI
- Let Vivado finish the rest of the routes

There is no logic outside of the ROI in order to keep IOB to ROI delays short
Its expected the end user will rip out everything inside the ROI

To target Arty A7 you should source the artix DB environment script then source arty.sh

To build the baseline harness:
```
./runme.sh
```

To build a sample Vivado design using the harness:
```
XRAY_ROIV=roi_inv.v XRAY_FIXED_XDC=out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev/fixed_noclk.xdc ./runme.sh
```
Note: this was intended for verification only and not as an end user flow (they should use SymbiFlow)

To use the harness for the basys3 demo, do something like:
```
python3 demo_sw_led.py out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev 3 2
```
This example connects switch 3 to LED 2

## Result
