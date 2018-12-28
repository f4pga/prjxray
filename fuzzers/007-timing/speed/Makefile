all: build/speed.json

build/node.txt: speed_json.py generate.tcl
	mkdir -p build
	cd build && ${XRAY_VIVADO} -mode batch -source ../generate.tcl

build/speed.json: build/node.txt
	cd build && python ../speed_json.py speed_model.txt node.txt speed.json

clean:
	rm -rf build

