all: build/slicel.json build/slicem.json

clean:
	rm -rf build

build/slicel.json: build/slicel.txt
	python3 tim2sdf.py --timings build/slicel.txt --json build/slicel.json

build/slicem.json: build/slicem.txt
	python3 tim2sdf.py --timings build/slicem.txt --json build/slicem.json

build/slicel.txt build/slicem.txt:
	bash runme.sh

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings

