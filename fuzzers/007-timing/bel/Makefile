all: build/sdf.ok

clean:
	rm -rf build

build/bel_timings.txt:
	bash runme.sh

build/fixup_timings: build/bel_timings.txt
	python3 fixup_timings_txt.py --txtin build/bel_timings.txt --txtout build/bel_timings.txt --site RAMBFIFO36E1 --slice BRAM_L --type timings
	python3 fixup_timings_txt.py --txtin build/bel_timings.txt --txtout build/bel_timings.txt --site RAMBFIFO36E1 --slice BRAM_R --type timings
	python3 fixup_timings_txt.py --txtin build/bel_pins.txt --txtout build/bel_pins.txt --site RAMBFIFO36E1 --slice BRAM_L --type pins
	python3 fixup_timings_txt.py --txtin build/bel_pins.txt --txtout build/bel_pins.txt --site RAMBFIFO36E1 --slice BRAM_R --type pins
	python3 fixup_timings_txt.py --txtin build/bel_properties.txt --txtout build/bel_properties.txt --site RAMBFIFO36E1 --slice BRAM_L --type properties
	python3 fixup_timings_txt.py --txtin build/bel_properties.txt --txtout build/bel_properties.txt --site RAMBFIFO36E1 --slice BRAM_R --type properties

build/bel_timings.json: build/fixup_timings
	python3 tim2json.py --timings=build/bel_timings.txt --json=build/bel_timings.json --properties=build/bel_properties.txt --propertiesmap=properties_map.json --pinaliasmap=pin_alias_map.json --belpins=build/bel_pins.txt --sitepins=build/tile_pins.txt --debug true

build/sdf.ok: build/bel_timings.json
	python3 ${XRAY_UTILS_DIR}/makesdf.py --json=${PWD}/build/bel_timings.json --sdf=${PWD}/build
	touch build/sdf.ok

