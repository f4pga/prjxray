clean:
	for d in $$(find fuzzers minitests experiments -name Makefile -type f); do \
		(cd $$(dirname $$d) && $(MAKE) clean) || true; \
	done

