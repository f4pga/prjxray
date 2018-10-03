N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

all: $(SPECIMENS_OK)

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@) || (if [ "$(BADPRJ_OK)" != 'Y' ] ; then exit 1; fi; exit 0)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) all
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits __pycache__ run.ok
	rm -rf vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit
	rm -rf build

.PHONY: all run clean

