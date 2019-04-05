# Minimal makefile for Sphinx documentation
#

MAKEDIR := $(dir $(lastword $(MAKEFILE_LIST)))

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
	@cd $(MAKEDIR)/db_dev_process/fuzzers && rm -f *.md
	@cd $(MAKEDIR)/db_dev_process/fuzzers && \
		for i in ../../../fuzzers/*; do \
			n=$$(basename $$i | sed -e's/^[0-9][0-9][0-9]-//'); \
			if [ ! -d $$i ]; then \
				continue; \
			fi; \
			if [ -e $$i/README.md ]; then \
				echo "Linking $$i/README.md"; \
				ln -s $$i/README.md $${n}.md; \
			else \
				echo "Missing $$i/README.md"; \
				echo "# $$n Fuzzer"		>  $${n}.md; \
				echo "" 			>> $${n}.md; \
				echo "Missing README.md!" 	>> $${n}.md; \
			fi; \
		done

minitests-links:
	@cd  $(MAKEDIR)/db_dev_process/minitests && rm -f *.md
	@cd  $(MAKEDIR)/db_dev_process/minitests && \
		for i in ../../../minitests/*; do \
			n=$$(basename $$i | sed -e's/^[0-9][0-9][0-9]-//'); \
			if [ ! -d $$i ]; then \
				continue; \
			fi; \
			if [ -e $$i/README.md ]; then \
				echo "Linking $$i/README.md"; \
				ln -s $$i/README.md $${n}.md; \
			else \
				echo "Missing $$i/README.md"; \
				echo "# $$n Minitest"		>  $${n}.md; \
				echo "" 			>> $${n}.md; \
				echo "Missing README.md!" 	>> $${n}.md; \
			fi; \
		done

links: fuzzers-links minitests-links
	@true

.PHONY: fuzzers-links minitests-links links

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile links
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
