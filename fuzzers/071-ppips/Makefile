
N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	cp build/specimen_001/ppips_clblm_l.txt build/
	cp build/specimen_001/ppips_clblm_r.txt build/
	cp build/specimen_001/ppips_clbll_l.txt build/
	cp build/specimen_001/ppips_clbll_r.txt build/
	cp build/specimen_001/ppips_int_l.txt build/
	cp build/specimen_001/ppips_int_r.txt build/

pushdb:
	cp build/ppips_clblm_l.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clblm_l.db
	cp build/ppips_clblm_r.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clblm_r.db
	cp build/ppips_clbll_l.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clbll_l.db
	cp build/ppips_clbll_r.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clbll_r.db
	cp build/ppips_int_l.txt   ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_int_l.db
	cp build/ppips_int_r.txt   ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_int_r.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

