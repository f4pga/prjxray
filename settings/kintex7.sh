export XRAY_DATABASE="kintex7"
export XRAY_PART="xc7k70tfbg676-2"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# FIXME: make entire part
export XRAY_ROI_TILEGRID="SLICE_X0Y50:SLICE_X19Y99 DSP48_X0Y20:DSP48_X0Y39 RAMB18_X0Y20:RAMB18_X0Y39 RAMB36_X0Y10:RAMB36_X0Y19"

# These settings must remain in sync
export XRAY_ROI="SLICE_X0Y50:SLICE_X19Y99 DSP48_X0Y20:DSP48_X0Y39 RAMB18_X0Y20:RAMB18_X0Y39 RAMB36_X0Y10:RAMB36_X0Y19 IOB_X0Y50:IOB_X0Y99"
# Part of CMT X0Y1
export XRAY_ROI_GRID_X1="0"
export XRAY_ROI_GRID_X2="38"
# Include VBRK / VTERM
export XRAY_ROI_GRID_Y1="104"
export XRAY_ROI_GRID_Y2="156"

# Choose the first N High Range I/Os
export XRAY_PIN_00="K25"
export XRAY_PIN_01="K26"
export XRAY_PIN_02="L24"
export XRAY_PIN_03="L25"
export XRAY_PIN_04="M19"
export XRAY_PIN_05="M20"
export XRAY_PIN_06="M21"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment_xc7.sh
