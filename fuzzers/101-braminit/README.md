FIXME: ROI is SLICE_X12Y100:SLICE_X27Y149
But we need something with BRAM

export XRAY_ROI=SLICE_X6Y100:SLICE_X27Y149
# Needed?
# export XRAY_ROI_FRAMES="0x00020500:0x000208ff"
source $XRAY_DIR/utils/environment.sh


Solves SLICEM specific bits:
-Shift register LUT (SRL)
-Memory size
-RAM vs LUT
-Related muxes

