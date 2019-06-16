
DATABASE_FILES = *.csv *.db *.json *.yaml
TIMINGS_FILES = *.sdf

clean-artix7-db:
	rm -f $(addprefix artix7/,$(DATABASE_FILES))
	rm -f $(addprefix artix7/timings/,$(TIMINGS_FILES))

clean-kintex7-db:
	rm -f $(addprefix kintex7/,$(DATABASE_FILES))
	rm -f $(addprefix kintex7/timings/,$(TIMINGS_FILES))

clean-zynq7-db:
	rm -f $(addprefix zynq7/,$(DATABASE_FILES))
	rm -f $(addprefix zynq7/timings/,$(TIMINGS_FILES))

clean-db: clean-artix7-db clean-kintex7-db clean-zynq7-db
	@true

clean: clean-db
	@true

.PHONY: clean-artix7-db clean-kintex7-db clean-zynq7-db clean-db clean

reset:
	git reset --hard

.PHONY: reset

update:
	git stash
	git fetch origin
	git merge origin/master
	git stash pop

.PHONY: update
