Creates an ROI with clk, inputs, and outputs to use as a partial reconfiguration test harness 

Basic idea:
-LOC LUTs in the ROI to terminate input and output routing
-Let Vivado LOC the rest of the logic
-Manually route signals in and out of the ROI enough to avoid routing loops into the ROI
-Let Vivado finish the rest of the routes

There is no logic outside of the ROI in order to keep IOB to ROI delays short
Its expected the end user will rip out everything inside the ROI

To target Arty A7 you should source the artix DB environment script then source arty.sh
