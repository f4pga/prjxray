set -ex

BIT_IN=$1
BITS=$(tempfile --suffix .bits)

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${BITS} -z -y ${BIT_IN}
${XRAY_DIR}/utils/bits2fasm.py ${BITS}
