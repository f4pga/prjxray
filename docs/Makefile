# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAUTOBUILD   = sphinx-autobuild
SPHINXPROJ    = ProjectX-Ray
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml:
	@$(SPHINXAUTOBUILD) -b html --ignore \*.swp --ignore \*~ $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/html"

.PHONY: help livereload Makefile

# Update fuzzer / minitest markdown links.
fuzzers-links:
	@cd db_dev_process/fuzzers; rm -f *.md
	@cd db_dev_process/fuzzers; \
		for i in ../../../fuzzers/*; do \
			if [ ! -d $$i ]; then \
				continue; \
			fi; \
			if [ -e $$i/README.md ]; then \
				echo "Linking $$i/README.md"; \
				ln -s $$i/README.md $$(basename $$i).md; \
			else \
				echo "Missing $$i/README.md"; \
				echo "# $$(basename $$i)" 	> $$(basename $$i).md; \
				echo "" 			>> $$(basename $$i).md; \
				echo "Missing README.md!" 	>> $$(basename $$i).md; \
			fi; \
		done

minitests-links:
	@cd db_dev_process/minitests; rm -f *.md
	@cd db_dev_process/minitests; \
		for i in ../../../minitests/*; do \
			if [ ! -d $$i ]; then \
				continue; \
			fi; \
			if [ -e $$i/README.md ]; then \
				echo "Linking $$i/README.md"; \
				ln -s $$i/README.md $$(basename $$i).md; \
			else \
				echo "Missing $$i/README.md"; \
				echo "# $$(basename $$i)" 	> $$(basename $$i).md; \
				echo "" 			>> $$(basename $$i).md; \
				echo "Missing README.md!" 	>> $$(basename $$i).md; \
			fi; \
		done

links: fuzzers-links minitests-links
	@true

.PHONY: fuzzers-links minitests-links links

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile links
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
