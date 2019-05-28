all: pushdb

clean:
	rm -rf build

build/bel_timings.txt:
	bash runme.sh

build/bel_timings.json: build/bel_timings.txt
	python3 tim2json.py --timings=build/bel_timings.txt --json=build/bel_timings.json --properties=build/bel_properties.txt --propertiesmap=properties_map.json --pinaliasmap=pin_alias_map.json --belsuffixmap=bel_suffix_map.json --belpins=build/bel_pins.txt --sitepins=build/tile_pins.txt --debug true

build/sdf: build/bel_timings.json
	python3 ${XRAY_UTILS_DIR}/makesdf.py --json=${PWD}/build/bel_timings.json --sdf=${PWD}/build

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings

mergesdfs: build/sdf
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs build/CLBLL_L.sdf build/CLBLL_R.sdf build/CLBLM_L.sdf build/CLBLM_R.sdf --site SLICEM --out build/slicem.sdf
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs build/CLBLL_L.sdf build/CLBLL_R.sdf build/CLBLM_L.sdf build/CLBLM_R.sdf --site SLICEL --out build/slicel.sdf

pushdb: mergesdfs
	mkdir -p ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	cp build/*sdf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	touch run.ok
