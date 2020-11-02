DB_ROOT ?= ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}
PART ?= ${XRAY_PART}
DATABASE ?= build_${PART}/${PART}.db
WIRE_PATTERNS ?= build_${PART}/wire_patterns.bin

all: build_${PART}/wire_patterns.bin

build_${PART}:
	mkdir -p build_${PART}

${DATABASE}: build_node_lookup.py node_lookup.py | build_${PART}
	python3 build_node_lookup.py \
		--db-root ${DB_ROOT} \
		--part ${PART} \
		${DATABASE}

${WIRE_PATTERNS}: test_reduction.py ${DATABASE}
	python3 test_reduction.py \
		--database ${DATABASE} \
		--wire_patterns ${WIRE_PATTERNS}

.PHONY: clean

clean:
	rm -rf build_${PART}
