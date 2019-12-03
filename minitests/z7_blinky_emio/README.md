# Zynq7 EMIO minitest

This is a simple test of PS -> PL interface for Zynq7. Works on the ZYBO Z7 board with xc7z020 but should also work for xc7z010.

The PS firmware is bare metal. Upon start it enables MIO7 as output as well as PS <-> PL level shifters. Next it implements a blinking led on MIO7 and counter on GPIO bank 2. The bank 2 is connected to EMIOGPIOO[31:0] signals of the PS7 instance in the PL logic design.

The PL design "instantiates" the PS7 and connects EMIOGPIOO[3:0] to LEDs LD0-LD3 but through XOR gates controlled by push buttons BTN0-BTN3.

# Building & loading

## PS

Run `make firmware` to compile the firmware. Then run `make run` to upload it to Zybo. You must have Xilinx XSCT installed and pointed to in the environment. You can also just run `make` to execute those two above steps. Upon loading the LED LD4 should start blinking.

## PL

Run `make top.bit` to generate the bitstream. Upload it to the Zybo AFTER uploading and running PS firmware. You can use eg. xc3sprog with the following command `xc3sprog -c jtaghs1 -p 1 top.bit`. Once done LEDs LD0-LD3 should begin dusplaying 4 LSBs of the counter.

