export XRAY_DATABASE="artix7"
export XRAY_PART="xc7a100tfgg676-1"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
# tcl queries IOB => don't bother adding
export XRAY_ROI_TILEGRID="RAMB36_X0Y0:RAMB36_X3Y39 RAMB18_X0Y0:RAMB18_X3Y79 DSP48_X0Y0:DSP48_X2Y79 IOB_X0Y0:IOB_X1Y199 SLICE_X0Y0:SLICE_X89Y199"

export XRAY_EXCLUDE_ROI_TILEGRID=""

export XRAY_IOI3_TILES="RIOI3_X57Y109 LIOI3_X0Y109"

# clock pin
export XRAY_PIN_00="Y22"
# data pins
export XRAY_PIN_01="U17"
export XRAY_PIN_02="V17"
export XRAY_PIN_03="V16"
export XRAY_PIN_04="V14"
export XRAY_PIN_05="U14"
export XRAY_PIN_06="U16"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh

