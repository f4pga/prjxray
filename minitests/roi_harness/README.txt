Creates an ROI with clk, inputs, and outputs to use as a partial reconfiguration test harness 

Basic idea:
-LOC LUTs in the ROI to terminate input and output routing
-Let Vivado LOC the rest of the logic
-Manually route signals in and out of the ROI enough to avoid routing loops into the ROI
-Let Vivado finish the rest of the routes

There is no logic outside of the ROI in order to keep IOB to ROI delays short
Its expected the end user will rip out everything inside the ROI

To target Arty A7 you should source the artix DB environment script then source arty.sh

To build the baseline harness:
./runme.sh

To build a sample Vivado design using the harness:
XRAY_ROIV=roi_inv.v XRAY_FIXED_XDC=out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev/fixed_noclk.xdc ./runme.sh
Note: this was intended for verification only and not as an end user flow (they should use SymbiFlow)

To use the harness for the basys3 demo, do something like:
python3 demo_sw_led.py out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev 3 2
This example connects switch 3 to LED 2
