all: build/slicel.sdf build/slicem.sdf

clean:
	rm -rf build

build/slicel.sdf: build/run.ok
	python3 tim2sdf.py --timings build/slicel.txt --site SLICEL --sdf build/slicel.sdf

build/slicem.sdf: build/run.ok
	python3 tim2sdf.py --timings build/slicem.txt --site SLICEM --sdf build/slicem.sdf

build/run.ok:
	bash runme.sh

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings

