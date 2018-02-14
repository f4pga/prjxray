.NOTPARALLEL:

SUBDIRS := $(patsubst %/,%, $(wildcard */))

.PHONY: $(SUBDIRS)

$(MAKECMDGOALS): $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ -f ../Makefile.database $(MAKECMDGOALS)
