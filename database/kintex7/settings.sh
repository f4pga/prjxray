source $(dirname ${BASH_SOURCE[0]})/../../utils/environment.sh

export XRAY_DATABASE="kintex7"
export XRAY_PART="xc7k70tfbg676-2"
export XRAY_ROI="SLICE_X24Y150:SLICE_X35Y199"
# FIXME: a7 value
export XRAY_ROI_FRAMES="0x00020500:0x000208ff"
export XRAY_ROI_GRID_X1="48"
export XRAY_ROI_GRID_X2="67"
export XRAY_ROI_GRID_Y1="0"
export XRAY_ROI_GRID_Y2="52"
# Choose the first N High Range I/Os
export XRAY_PIN_00="K25"
export XRAY_PIN_01="K26"
export XRAY_PIN_02="L24"
export XRAY_PIN_03="L25"
export XRAY_PIN_04="M19"
export XRAY_PIN_05="M20"
export XRAY_PIN_06="M21"
