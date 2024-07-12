# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

github:
	@make graphs
	mkdir source/prebuilt
	mkdir source/prebuilt/coverage
	mkdir source/prebuilt/pytest-html
	# pytest --cov-report html:source/prebuilt/coverage --cov=../src ../tests --html=source/prebuilt/pytest-html/report.html
	@make html
	@cp -a build/html/. ../docs


PYSOURCEDIR = ../src

graphs:
	cd ..; pyreverse sports_planner -d sphinx/source/graphviz;
