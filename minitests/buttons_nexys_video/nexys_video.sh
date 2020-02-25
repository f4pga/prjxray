
if [ -z ${XRAY_DIR+x} ]; then
    echo "XRAY_DIR not set!"
    return
fi

source ${XRAY_DIR}/settings/artix200t.sh
export XRAY_PART=xc7a200tsbg484-1
