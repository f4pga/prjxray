N ?= 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
ENV_VAR ?=
FUZDIR ?= ${PWD}

all: database

$(SPECIMENS_OK):
	mkdir -p build
	if [ -f $(FUZDIR)/generate.sh ]; then export $(ENV_VAR); bash $(FUZDIR)/generate.sh $(subst /OK,,$@); else bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@); fi

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: all run clean

