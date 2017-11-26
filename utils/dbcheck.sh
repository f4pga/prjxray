#!/bin/bash
python3 ${XRAY_UTILS_DIR}/dbcheck.py ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits_{clblm,int}_l.db
python3 ${XRAY_UTILS_DIR}/dbcheck.py ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits_{clblm,int}_r.db
python3 ${XRAY_UTILS_DIR}/dbcheck.py ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits_{clbll,int}_l.db
python3 ${XRAY_UTILS_DIR}/dbcheck.py ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits_{clbll,int}_r.db
