export XRAY_DATABASE="spartan6"
export XRAY_PART="xc6slx9-2-csg324"
#export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
#export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X43Y99 RAMB18_X0Y0:RAMB18_X2Y39 RAMB36_X0Y0:RAMB36_X2Y19 DSP48_X0Y0:DSP48_X1Y39"

# These settings must remain in sync
#export XRAY_ROI="SLICE_X00Y50:SLICE_X43Y99 RAMB18_X0Y20:RAMB18_X2Y39 RAMB36_X0Y10:RAMB36_X2Y19 IOB_X0Y50:IOB_X0Y99"

# Most of CMT X0Y2.
#export XRAY_ROI_GRID_X1="83"
#export XRAY_ROI_GRID_X2="118"
# Include VBRK / VTERM
#export XRAY_ROI_GRID_Y1="0"
#export XRAY_ROI_GRID_Y2="51"

export XRAY_PIN_00="P15"
export XRAY_PIN_01="P16"
export XRAY_PIN_02="M18"
export XRAY_PIN_03="L18"
export XRAY_PIN_04="F17"
export XRAY_PIN_05="F18"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment_sp6.sh
