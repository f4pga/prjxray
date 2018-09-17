all: build/timgrid.json

build/timgrid.txt: generate.tcl
	mkdir -p build
	cd build && vivado -mode batch -source ../generate.tcl

build/timgrid.json: build/timgrid.txt
	cd build && python3 ../tile_txt2json.py --speed-json ../../speed/build/speed.json timgrid.txt timgrid-s.json

clean:
	rm -rf build

