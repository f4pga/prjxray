# Unsetting all previous XRAY env variables
unset ${!XRAY_@}

export XRAY_DATABASE="xc7z"
export XRAY_PART="xc7z010clg400-1"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"
export XRAY_XC7Z="1"

# All CLB's in part, all BRAM's in part, all DSP's in part.
export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X43Y99 RAMB18_X0Y0:RAMB18_X2Y39 RAMB36_X0Y0:RAMB36_X2Y19 DSP48_X0Y0:DSP48_X1Y39"

# These settings must remain in sync
export XRAY_ROI="SLICE_X34Y0:SLICE_X43Y99 RAMB18_X2Y0:RAMB18_X2Y39 RAMB36_X2Y0:RAMB36_X2Y19 IOB_X0Y0:IOB_X0Y99"
# Most of CMT X0Y2.
export XRAY_ROI_GRID_X1="-1"
export XRAY_ROI_GRID_X2="-1"
# Include VBRK / VTERM
export XRAY_ROI_GRID_Y1="-1"
export XRAY_ROI_GRID_Y2="-1"

export XRAY_PIN_00="T11"
export XRAY_PIN_01="T10"
export XRAY_PIN_02="T12"
export XRAY_PIN_03="U12"
export XRAY_PIN_04="U13"
export XRAY_PIN_05="V13"
export XRAY_PIN_06="V12"

source $(dirname ${BASH_SOURCE[0]})/../../utils/environment.sh
