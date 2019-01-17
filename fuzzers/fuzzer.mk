N ?= 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
ENV_VAR ?=
VAR ?=
ITER ?= 0
MAX_ITER ?= 10

all: database

$(SPECIMENS_OK):
	mkdir -p build
	if [ -f `pwd`/generate.sh ]; then export $(ENV_VAR); bash `pwd`/generate.sh $(subst /OK,,$@); else bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@); fi

run:
	# If the database presents errors or is incomplete, the fuzzer is rerun.
	# When it reaches the maximum number of iterations it fails.
	@if [ $(ITER) -gt $(MAX_ITER) ]; then \
		echo "Max Iterations reached. Fuzzer unsolvable."; \
		exit 1; \
	fi
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb || $(MAKE) $(VAR) ITER=$$(($(ITER) + 1)) run
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: all run clean

