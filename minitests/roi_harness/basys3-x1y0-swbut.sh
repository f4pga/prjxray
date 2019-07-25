# XC7A35T-1CPG236C
export XRAY_PINCFG=BASYS3-X1Y0-SWBUT
export XRAY_DIN_N_LARGE=2
export XRAY_DOUT_N_LARGE=2
export HARNESS_DIR=$XRAY_DIR/database/artix7/harness/basys3/x1y0-swbut/
export XRAY_FIXED_XDC=../basys3-x1y0-fixed.xdc

source $XRAY_DIR/minitests/roi_harness/basys3-x1y0-common.sh
