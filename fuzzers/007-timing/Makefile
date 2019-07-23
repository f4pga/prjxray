SLICEL_SDFS = bel/build/slicel.sdf bel/build/carry4_slicel.sdf routing-bels/build/slicel.sdf
SLICEM_SDFS = bel/build/slicem.sdf bel/build/carry4_slicem.sdf routing-bels/build/slicem.sdf

run: all
all: pushdb

clean:
	cd bel && $(MAKE) clean
	cd routing-bels && $(MAKE) clean

bel/build/all_sdf.ok:
	cd bel && $(MAKE)

routing-bels/build/sdf.ok:
	cd routing-bels && $(MAKE)

mergesdfs: bel/build/all_sdf.ok routing-bels/build/sdf.ok
	mkdir -p sdfs
	cp bel/build/*.sdf sdfs
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEM_SDFS) --site SLICEM --out sdfs/slicem.sdf
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEL_SDFS) --site SLICEL --out sdfs/slicel.sdf

pushdb: mergesdfs
	mkdir -p ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	cp sdfs/*.sdf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	touch run.ok

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings

