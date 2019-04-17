all: build/sdf

clean:
	rm -rf build

build/bel_timings.txt:
	bash runme.sh

build/bel_timings.json: build/bel_timings.txt
	python3 tim2json.py --timings=build/bel_timings.txt --json=build/bel_timings.json --properties=build/bel_properties.txt --belpins=build/bel_pins.txt --sitepins=build/tile_pins.txt

build/sdf: build/bel_timings.json
	python3 ${XRAY_UTILS_DIR}/makesdf.py --json=${PWD}/build/bel_timings.json --sdf=${PWD}/build
	mkdir -p ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	cp build/*sdf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
	touch run.ok

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings
