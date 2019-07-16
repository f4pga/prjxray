SLICEL_SDFS = bel/build/CLBLL_L.sdf bel/build/CLBLL_R.sdf bel/build/CLBLM_L.sdf bel/build/CLBLM_R.sdf routing-bels/build/slicel.sdf
SLICEM_SDFS = bel/build/CLBLL_L.sdf bel/build/CLBLL_R.sdf bel/build/CLBLM_L.sdf bel/build/CLBLM_R.sdf routing-bels/build/slicem.sdf

run: all
all: pushdb

clean:
	cd bel && $(MAKE) clean
	cd routing-bels && $(MAKE) clean

bel/build/sdf.ok:
	cd bel && $(MAKE)

routing-bels/build/sdf:
	cd routing-bels && $(MAKE)

mergesdfs: bel/build/sdf.ok routing-bels/build/sdf
	mkdir -p sdfs
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEM_SDFS) --site SLICEM --out routing-bels/build/precarry_slicem.sdf
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEL_SDFS) --site SLICEL --out routing-bels/build/precarry_slicel.sdf
	python3 ${XRAY_UTILS_DIR}/carry4delays.py --input routing-bels/build/precarry_slicem.sdf --output routing-bels/build/carry4_slicem.sdf
	python3 ${XRAY_UTILS_DIR}/carry4delays.py --input routing-bels/build/precarry_slicel.sdf --output routing-bels/build/carry4_slicel.sdf
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs routing-bels/build/precarry_slicem.sdf routing-bels/build/carry4_slicem.sdf --site SLICEM --out sdfs/slicem.sdf
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs routing-bels/build/precarry_slicel.sdf routing-bels/build/carry4_slicel.sdf --site SLICEL --out sdfs/slicel.sdf --json debu.json
	cp bel/build/*.sdf sdfs

pushdb: mergesdfs
	mkdir -p ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	cp sdfs/*.sdf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	touch run.ok

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings

