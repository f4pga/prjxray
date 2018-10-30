set -ex

BIT_IN=$1
BITS=$(tempfile --suffix .bits)

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${BITS} -z -y ${BIT_IN} > /dev/null
${XRAY_BITS2FASM} ${BITS}
